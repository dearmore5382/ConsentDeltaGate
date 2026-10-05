"""Resumable Studionet E2E runner. It never writes private keys to artifacts."""
import base64
import ast
import hashlib
import json
import os
import time
from pathlib import Path

import requests
from genlayer_py import create_account, create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "0xC20fCbfE9fCF97624ED45cd17cF3Ec98cA82dEc2"
RPC = "https://studio.genlayer.com/api"
KEY_SOURCES = [ROOT.parent / "DAOProposalContextVerifier" / ".env.lifecycle",
               ROOT.parent / "EvidenceBasedGrantEscrow" / ".env.lifecycle"]
OUT = ROOT / "verification" / ("live-" + ADDRESS.lower() + ".json")


def rpc(method, params):
    last = None
    for attempt in range(8):
        try:
            response = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1,
                "method": method, "params": params}, timeout=90)
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                raise RuntimeError(str(payload["error"]))
            return payload["result"]
        except (requests.RequestException, ValueError) as error:
            last = error
            if attempt < 7:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError("RPC_UNAVAILABLE:" + str(last))


def view(method, args=None):
    encoded = serialize([calldata.encode({"method": method, "args": args or []}), b"\x00"])
    raw = rpc("gen_call", [{"type": "read", "to": ADDRESS,
        "from": "0x0000000000000000000000000000000000000001", "value": "0x0",
        "data": encoded, "transaction_hash_variant": "latest-final"}])
    return str(calldata.decode(bytes.fromhex(raw.removeprefix("0x"))))


def parse_view(value):
    if not value or not value.startswith("{"):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return ast.literal_eval(value)


def wait_final(tx_hash):
    deadline = time.monotonic() + 1200
    while time.monotonic() < deadline:
        tx = rpc("eth_getTransactionByHash", [tx_hash])
        if tx and tx.get("status") == "FINALIZED":
            return tx
        time.sleep(5)
    raise RuntimeError("FINALITY_TIMEOUT")


def tx_return(tx):
    receipts = (tx.get("consensus_data") or {}).get("leader_receipt") or []
    receipts = [receipts] if isinstance(receipts, dict) else receipts
    leaders = [item for item in receipts if item.get("mode") == "leader"]
    if not leaders or leaders[-1].get("execution_result") != "SUCCESS":
        raise RuntimeError("LEADER_EXECUTION_FAILED")
    result = leaders[-1].get("result")
    raw = base64.b64decode(result["raw"] if isinstance(result, dict) else result)
    if not raw or raw[0] != 0:
        raise RuntimeError("CONTRACT_EXECUTION_ERROR")
    return str(calldata.decode(raw[1:]))


def load_keys():
    values = {}
    for path in KEY_SOURCES:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.split("=", 1)
                    values.setdefault(key.strip(), value.strip())
    keys = [os.environ.get("WALLET_A_PRIVATE_KEY", values.get("WALLET_A_PRIVATE_KEY", "")),
            os.environ.get("WALLET_B_PRIVATE_KEY", values.get("WALLET_B_PRIVATE_KEY", ""))]
    if not all(keys):
        raise RuntimeError("TWO_LOCAL_ROLE_KEYS_REQUIRED")
    return keys


def document(label, risk):
    return json.dumps({"schema": "consent-document-v1", "study_ref": "TRIAL-LIVE-2026",
        "revision_label": label, "sections": [
            {"section_id": "RISK-1", "category": "RISK", "text": risk},
            {"section_id": "PROC-1", "category": "PROCEDURE", "text": "One blood draw is required."},
            {"section_id": "RIGHT-1", "category": "WITHDRAWAL", "text": "Participants may withdraw at any time."},
            {"section_id": "DATA-1", "category": "DATA_USE", "text": "Coded data is retained for five years."}
        ]}, separators=(",", ":"))


def main():
    local = (ROOT / "contracts" / "ConsentDeltaGate.py").read_bytes()
    deployed = base64.b64decode(rpc("gen_getContractCode", [ADDRESS]))
    if deployed != local:
        raise RuntimeError("SOURCE_PARITY_FAILED local=" + hashlib.sha256(local).hexdigest() +
                           " deployed=" + hashlib.sha256(deployed).hexdigest())
    keys = load_keys()
    accounts = [create_account(account_private_key="0x" + key.removeprefix("0x")) for key in keys]
    del keys
    if accounts[0].address.lower() == accounts[1].address.lower():
        raise RuntimeError("DISTINCT_ROLE_WALLETS_REQUIRED")
    clients = [create_client(chain=studionet, account=account) for account in accounts]
    journal = {"network": "studionet", "contract": ADDRESS,
        "source_sha256": hashlib.sha256(local).hexdigest(), "source_parity": True,
        "roles": {"study_authority": accounts[0].address, "trial_site": accounts[1].address},
        "deployer_role": "deployment_only", "steps": [], "complete": False}
    if OUT.exists():
        journal = json.loads(OUT.read_text(encoding="utf-8"))
    for item in journal["steps"]:
        if item["id"] == "H2-site-baseline-consent" and item.get("return") == "CONSENT_MUST_TARGET_CURRENT":
            item["id"] = "F2b-wrong-global-revision"
            item["expected"] = ["CONSENT_MUST_TARGET_CURRENT"]
    completed = {item["id"] for item in journal["steps"]}

    def send(step_id, actor, method, args, expected, read_method=None, read_args=None):
        if step_id in completed:
            return journal["steps"][[x["id"] for x in journal["steps"]].index(step_id)]["return"]
        tx_hash = str(clients[actor].write_contract(address=ADDRESS, function_name=method,
            args=args, value=0, leader_only=False))
        tx = wait_final(tx_hash)
        if tx.get("result_name") != "MAJORITY_AGREE":
            raise RuntimeError(step_id + ":CONSENSUS_FAILED:" + str(tx.get("result_name")))
        actual = tx_return(tx)
        allowed = expected if isinstance(expected, tuple) else (expected,)
        state = view(read_method, read_args) if read_method else None
        entry = {"id": step_id, "actor": accounts[actor].address, "method": method, "args": args,
            "return": actual, "expected": list(allowed), "tx_hash": tx_hash,
            "explorer": "https://explorer-studio.genlayer.com/tx/" + tx_hash,
            "status": tx.get("status"), "consensus": tx.get("result_name"),
            "readback": parse_view(state)}
        journal["steps"].append(entry)
        OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
        if actual not in allowed:
            raise RuntimeError(step_id + ":UNEXPECTED_RETURN:" + actual)
        completed.add(step_id)
        return actual

    baseline = document("V1", "The known risks are headache and fatigue.")
    material = document("V2", "A newly identified cardiac risk may require additional monitoring.")
    subject = hashlib.sha256(b"live-pseudonymous-subject-2026").hexdigest()
    artifact_v1 = hashlib.sha256(b"signed-consent-artifact-v1").hexdigest()
    artifact_v2 = hashlib.sha256(b"signed-consent-artifact-v2").hexdigest()

    send("F1-invalid-same-role", 0, "create_study", ["TRIAL-BAD", accounts[0].address, baseline], "INVALID_STUDY")
    study = int(send("H1-create-study", 0, "create_study",
        ["TRIAL-LIVE-2026", accounts[1].address, baseline], ("0", "1")))
    baseline_revision = study
    send("F2-outsider-site-action", 0, "record_consent", [study, subject, 0, artifact_v1], "SITE_ONLY")
    send("H2-site-baseline-consent", 1, "record_consent", [study, subject, baseline_revision, artifact_v1],
        "CONSENT_RECORDED", "get_subject", [study, subject])
    send("H3-confirm-baseline", 1, "confirm_eligibility", [study, subject],
        "ELIGIBILITY_CONFIRMED", "get_subject", [study, subject])
    revision = int(send("H4-propose-material-revision", 0, "propose_revision", [study, baseline_revision, material],
        ("1", "2")))
    send("F3-confirm-before-assessment", 1, "confirm_eligibility", [study, subject],
        "REVIEW_INCOMPLETE", "get_subject", [study, subject])
    send("F4-site-cannot-propose", 1, "propose_revision", [study, baseline_revision, material], "AUTHORITY_ONLY")
    send("H5-consensus-assessment", 1, "assess_transition", [study, revision],
        "RECONSENT_REQUIRED", "get_revision", [revision])
    send("C1-material-block", 1, "confirm_eligibility", [study, subject],
        "BLOCKED_PENDING_RECONSENT", "get_subject", [study, subject])
    send("F5-artifact-replay", 1, "record_consent", [study, subject, revision, artifact_v1],
        "ARTIFACT_ALREADY_USED", "get_subject", [study, subject])
    send("H6-site-reconsent", 1, "record_consent", [study, subject, revision, artifact_v2],
        "CONSENT_RECORDED", "get_subject", [study, subject])
    send("H7-confirm-current", 0, "confirm_eligibility", [study, subject],
        "ELIGIBILITY_CONFIRMED", "get_subject", [study, subject])
    send("H8-close-study", 0, "close_study", [study], "STUDY_CLOSED", "get_study", [study])
    send("F6-write-after-close", 1, "record_consent", [study, "99" * 32, revision, "88" * 32],
        "STUDY_NOT_ACTIVE", "get_study", [study])
    journal["final_study"] = parse_view(view("get_study", [study]))
    journal["final_revision"] = parse_view(view("get_revision", [revision]))
    journal["final_subject"] = parse_view(view("get_subject", [study, subject]))
    journal["complete"] = True
    OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
    print("E2E_COMPLETE", OUT)


if __name__ == "__main__":
    main()
