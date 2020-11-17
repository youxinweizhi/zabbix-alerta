import textwrap
import unittest
from types import SimpleNamespace

from zabbix_alerta import parse_zabbix


class SenderTestCase(unittest.TestCase):
    def setUp(self) -> None:

        self.summary = '''{TRIGGER.STATUS}: {TRIGGER.NAME}'''
        self.body = '''
            resource={HOST.NAME1}
            event={ITEM.KEY1}
            environment=Production
            severity={TRIGGER.SEVERITY}!!
            status={TRIGGER.STATUS}
            ack={EVENT.ACK_STATUS}
            service={TRIGGER.HOSTGROUP_NAME}
            group=Zabbix
            value={ITEM.VALUE1}
            text={TRIGGER.STATUS}: {TRIGGER.NAME}
            tags={EVENT.TAGS}
            attributes.ip={HOST.IP1}
            attributes.thresholdInfo={TRIGGER.TEMPLATE_NAME}: {TRIGGER.EXPRESSION}
            attributes.moreInfo=<a href="http://x.x.x.x/tr_events.php?triggerid={TRIGGER.ID}&eventid={EVENT.ID}">Zabbix console</a>
            type=zabbixAlert
            dateTime={EVENT.DATE}T{EVENT.TIME}Z
        '''

    def tearDown(self) -> None:
        pass

    def test_parser_macros(self):

        trigger = {
            'ID': 1,
            'STATUS': 'PROBLEM',
            'NAME': 'PSU-0.40: Temperature is above threshold',
            'SEVERITY': 'warning',
            'TEMPLATE_NAME': 'template',
            'EXPRESSION': 'expr',
            'HOSTGROUP_NAME': 'group1',
        }
        host = {'NAME1': 'hostname1', 'IP1': '10.1.1.1'}
        item = {'KEY1': 'e4597efc-3811-4476-9cf5-4e9d8501037e', 'VALUE1': '61°'}
        event = {'ID': 2, 'DATE': '', 'TIME': '', 'ACK_STATUS': '', 'TAGS': 'tag1,tag2'}
        summary = self.summary.format(TRIGGER=SimpleNamespace(**trigger))
        body = textwrap.dedent(
            self.body.format(
                HOST=SimpleNamespace(**host),
                ITEM=SimpleNamespace(**item),
                TRIGGER=SimpleNamespace(**trigger),
                EVENT=SimpleNamespace(**event),
            )
        )

        alert = parse_zabbix(summary, body)
        print(alert)

        assert alert['resource'] == 'hostname1'
        assert alert['event'] == 'e4597efc-3811-4476-9cf5-4e9d8501037e'
        assert alert['environment'] == 'Production'
        assert alert['severity'] == 'warning'
        assert alert['service'] == ['group1']
        assert alert['group'] == 'Zabbix'
        assert alert['value'] == '61°'
        assert alert['text'] == 'PROBLEM: PSU-0.40: Temperature is above threshold'
        # assert alert['tags'] == ['tag1', 'tag2']
        assert alert['attributes'] == {
            'ip': '10.1.1.1',
            'moreInfo': '<a href="http://x.x.x.x/tr_events.php?triggerid=1&eventid=2">Zabbix console</a>',
            'thresholdInfo': 'template: expr',
        }
        assert alert['origin'].startswith('zabbix/')
        assert alert['type'] == 'zabbixAlert'