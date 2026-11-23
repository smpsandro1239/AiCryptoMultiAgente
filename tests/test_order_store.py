from multiagent_trading.core.order_store import OrderStore


def test_order_store_persists_unique_order_ids_across_instances(tmp_path):
    database = tmp_path / "orders.sqlite3"
    first = OrderStore(str(database))
    assert first.reserve("order-1", {"symbol": "BTC/USDT"})
    assert first.get("order-1")["status"] == "pending"
    first.close()

    second = OrderStore(str(database))
    assert not second.reserve("order-1", {"symbol": "BTC/USDT"})
    assert second.set_status("order-1", "filled", {"fill_price": 100})
    assert second.get("order-1")["payload"] == {"fill_price": 100}
    assert not second.set_status("order-1", "rejected", {"reason": "late update"})
    second.close()


def test_order_store_keeps_stale_pending_claims_fail_closed(tmp_path):
    database = tmp_path / "orders.sqlite3"
    first = OrderStore(str(database))
    assert first.reserve("uncertain-order", {"symbol": "ETH/USDT"})
    first.close()

    restarted = OrderStore(str(database))
    assert not restarted.reserve("uncertain-order", {"symbol": "ETH/USDT"})
    assert restarted.get("uncertain-order")["status"] == "pending"
    restarted.close()


def test_order_store_rejects_invalid_status():
    store = OrderStore()
    assert store.reserve("order-2", {})
    try:
        store.set_status("order-2", "cancelled")
    except ValueError as error:
        assert "Estado final" in str(error)
    else:
        raise AssertionError("Estado inválido deveria ser rejeitado.")
    store.close()
