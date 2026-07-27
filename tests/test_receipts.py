from ignis.receipts import ReceiptSigner, new_receipt


def test_receipt_round_trip_and_tamper_detection():
    signer = ReceiptSigner(b"k" * 32, key_id="test")
    receipt = new_receipt("repair.example", status="planned", plan=[], evidence={})
    envelope = signer.sign(receipt)
    assert signer.verify(envelope)
    envelope["payload"]["status"] = "succeeded"
    assert not signer.verify(envelope)


def test_short_signing_key_is_rejected():
    try:
        ReceiptSigner(b"short")
    except ValueError as error:
        assert "32 bytes" in str(error)
    else:
        raise AssertionError("short key was accepted")
