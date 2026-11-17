# SPDX-License-Identifier: GPL-3.0-or-later
from simdesk.core.modem import read_info


def test_info_reads_identity_network_and_signal(fake_object):
    info = read_info(fake_object)

    assert info.path == "/org/freedesktop/ModemManager1/Modem/0"
    assert info.manufacturer == "QUALCOMM INCORPORATED"
    assert info.model == "Snapdragon X55"
    assert info.revision == "SDX55-1.0"
    assert info.imei == "860000000000001"
    assert info.imsi == "624010000000001"
    assert info.state == "registered"
    assert info.operator_name == "MTN CM"
    assert info.operator_code == "62401"
    assert info.access_technologies == "lte"
    assert info.signal_quality == 72
    assert info.signal_recent is True


def test_info_without_sim_has_no_imsi(fake_object):
    fake_object.modem.sim_path = "/"

    assert read_info(fake_object).imsi is None


def test_info_when_sim_read_fails_has_no_imsi(fake_object):
    fake_object.modem.sim_error = True

    assert read_info(fake_object).imsi is None


def test_info_on_non_3gpp_modem_has_no_imei_or_operator(fake_object):
    fake_object.modem_3gpp = None

    info = read_info(fake_object)

    assert info.imei is None
    assert info.operator_name is None
    assert info.operator_code is None


def test_empty_operator_name_becomes_none(fake_object):
    fake_object.modem_3gpp.operator_name = ""

    assert read_info(fake_object).operator_name is None
