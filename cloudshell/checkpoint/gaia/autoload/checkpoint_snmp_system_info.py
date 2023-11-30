from __future__ import annotations

from cloudshell.snmp.autoload.services.system_info_table import SnmpSystemInfo
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject


class CheckpointSNMPSystemInfo(SnmpSystemInfo):
    def _get_device_model(self):
        """Get device model from the SNMPv2 mib."""
        result = self._get_val(
            self._snmp_handler.get_property(
                SnmpMibObject("CHECKPOINT-MIB", "svnApplianceProductName", "0")
            )
        )

        return result

    def _get_vendor(self):
        """Get device model from the SNMPv2 mib."""
        if not self._vendor:
            sys_obj_id = self._snmp_v2_obj.get_system_object_id()
            sys_obj_id_oid = str(sys_obj_id.raw_value)
            oid_match = self.VENDOR_OID_PATTERN.search(sys_obj_id_oid)
            if oid_match:
                self._vendor = self._snmp_handler.translate_oid(
                    oid_match.group()
                ).capitalize()

        return self._vendor or "Checkpoint"

    def _get_device_os_version(self) -> str:
        """Get device OS Version form snmp SNMPv2 mib."""
        result = self._get_val(
            self._snmp_handler.get_property(
                SnmpMibObject("CHECKPOINT-MIB", "svnVersion", "0")
            )
        )

        return result

    def is_valid_device_os(self, supported_os: list[str]) -> bool:
        """Validate device OS using snmp."""
        if not SnmpSystemInfo.is_valid_device_os(self, supported_os=supported_os):
            # Check is vendor equal Checkpoint
            return self._get_vendor().lower() == "checkpoint"

        return True
