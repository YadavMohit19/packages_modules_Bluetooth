# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from mmi2grpc._helpers import assert_description
from mmi2grpc._proxy import ProfileProxy

from pandora.gatt_grpc import GATT
from pandora.host_grpc import Host

# Tests that need GATT cache cleared before discovering services.
NEEDS_CACHE_CLEARED = {
    "GATT/CL/GAD/BV-01-C",
    "GATT/CL/GAD/BV-06-C",
}


class GATTProxy(ProfileProxy):

    def __init__(self, channel):
        super().__init__()
        self.gatt = GATT(channel)
        self.host = Host(channel)
        self.connection = None
        self.services = None
        self.characteristics = None
        self.descriptors = None

    @assert_description
    def MMI_IUT_INITIATE_CONNECTION(self, test, pts_addr: bytes, **kwargs):
        """
        Please initiate a GATT connection to the PTS.

        Description: Verify that
        the Implementation Under Test (IUT) can initiate GATT connect request to
        PTS.
        """

        self.connection = self.host.ConnectLE(address=pts_addr).connection
        if test in NEEDS_CACHE_CLEARED:
            self.gatt.ClearCache(connection=self.connection)
        return "OK"

    @assert_description
    def MMI_IUT_INITIATE_DISCONNECTION(self, **kwargs):
        """
        Please initiate a GATT disconnection to the PTS.

        Description: Verify
        that the Implementation Under Test (IUT) can initiate GATT disconnect
        request to PTS.
        """

        assert self.connection is not None
        self.host.DisconnectLE(connection=self.connection)
        self.connection = None
        self.services = None
        self.characteristics = None
        self.descriptors = None
        return "OK"

    @assert_description
    def MMI_IUT_MTU_EXCHANGE(self, **kwargs):
        """
        Please send exchange MTU command to the PTS.

        Description: Verify that
        the Implementation Under Test (IUT) can send Exchange MTU command to the
        tester.
        """

        assert self.connection is not None
        self.gatt.ExchangeMTU(mtu=512, connection=self.connection)
        return "OK"

    def MMI_IUT_SEND_PREPARE_WRITE_REQUEST_VALID_SIZE(self, description: str, **kwargs):
        """
        Please send prepare write request with handle = 'XXXX'O and size = 'XXX'
        to the PTS.

        Description: Verify that the Implementation Under Test
        (IUT) can send data according to negotiate MTU size.
        """

        assert self.connection is not None
        matches = re.findall("'([a0-Z9]*)'O and size = '([a0-Z9]*)'", description)
        handle = int(matches[0][0], 16)
        data = bytes([1]) * int(matches[0][1])
        self.gatt.WriteCharacteristicFromHandle(connection=self.connection,\
                handle=handle, value=data)
        return "OK"

    @assert_description
    def MMI_IUT_DISCOVER_PRIMARY_SERVICES(self, **kwargs):
        """
        Please send discover all primary services command to the PTS.
        Description: Verify that the Implementation Under Test (IUT) can send
        Discover All Primary Services.
        """

        assert self.connection is not None
        self.services = self.gatt.DiscoverServices(connection=self.connection).services
        return "OK"

    def MMI_SEND_PRIMARY_SERVICE_UUID(self, description: str, **kwargs):
        """
        Please send discover primary services with UUID value set to 'XXXX'O to
        the PTS.

        Description: Verify that the Implementation Under Test (IUT)
        can send Discover Primary Services UUID = 'XXXX'O.
        """

        assert self.connection is not None
        uuid = formatUuid(re.findall("'([a0-Z9]*)'O", description)[0])
        self.services = self.gatt.DiscoverServiceByUuid(connection=self.connection,\
                uuid=uuid).services
        return "OK"

    def MMI_SEND_PRIMARY_SERVICE_UUID_128(self, description: str, **kwargs):
        """
        Please send discover primary services with UUID value set to
        'XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX'O to the PTS.

        Description:
        Verify that the Implementation Under Test (IUT) can send Discover
        Primary Services UUID = 'XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX'O.
        """

        assert self.connection is not None
        uuid = formatUuid(re.findall("'([a0-Z9-]*)'O", description)[0])
        self.services = self.gatt.DiscoverServiceByUuid(connection=self.connection,\
                uuid=uuid).services
        return "OK"

    def MMI_CONFIRM_PRIMARY_SERVICE_UUID(self, **kwargs):
        """
        Please confirm IUT received primary services uuid = 'XXXX'O , Service
        start handle = 'XXXX'O, end handle = 'XXXX'O in database. Click Yes if
        IUT received it, otherwise click No.

        Description: Verify that the
        Implementation Under Test (IUT) can send Discover primary service by
        UUID in database.
        """

        # Android doesn't store services discovered by UUID.
        return "Yes"

    @assert_description
    def MMI_CONFIRM_NO_PRIMARY_SERVICE_SMALL(self, **kwargs):
        """
        Please confirm that IUT received NO service uuid found in the small
        database file. Click Yes if NO service found, otherwise click No.
        Description: Verify that the Implementation Under Test (IUT) can send
        Discover primary service by UUID in small database.
        """

        # Android doesn't store services discovered by UUID.
        return "Yes"

    def MMI_CONFIRM_PRIMARY_SERVICE_UUID_128(self, **kwargs):
        """
        Please confirm IUT received primary services uuid=
        'XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX'O, Service start handle =
        'XXXX'O, end handle = 'XXXX'O in database. Click Yes if IUT received it,
        otherwise click No.

        Description: Verify that the Implementation Under
        Test (IUT) can send Discover primary service by UUID in database.
        """

        # Android doesn't store services discovered by UUID.
        return "Yes"

    def MMI_CONFIRM_PRIMARY_SERVICE(self, description: str, **kwargs):
        """
        Please confirm IUT received primary services Primary Service = 'XXXX'O
        Primary Service = 'XXXX'O  in database. Click Yes if IUT received it,
        otherwise click No.

        Description: Verify that the Implementation Under
        Test (IUT) can send Discover all primary services in database.
        """

        assert self.services is not None
        all_matches = list(map(formatUuid, re.findall("'([a0-Z9]*)'O", description)))
        assert all(uuid in list(map(lambda service: service.uuid, self.services))\
                for uuid in all_matches)
        return "OK"

    @assert_description
    def MMI_IUT_FIND_INCLUDED_SERVICES(self, **kwargs):
        """
        Please send discover all include services to the PTS to discover all
        Include Service supported in the PTS. Discover primary service if
        needed.

        Description: Verify that the Implementation Under Test (IUT)
        can send Discover all include services command.
        """

        assert self.connection is not None
        self.services = self.gatt.DiscoverServices(connection=self.connection).services
        return "OK"

    @assert_description
    def MMI_CONFIRM_NO_INCLUDE_SERVICE(self, **kwargs):
        """
        There is no include service in the database file.

        Description: Verify
        that the Implementation Under Test (IUT) can send Discover all include
        services in database.
        """

        assert self.connection is not None
        assert self.services is not None
        for service in self.services:
            assert len(service.included_services) is 0
        return "OK"

    def MMI_CONFIRM_INCLUDE_SERVICE(self, description: str, **kwargs):
        """
        Please confirm IUT received include services:

        Attribute Handle = 'XXXX'O, Included Service Attribute handle = 'XXXX'O,
        End Group Handle = 'XXXX'O, Service UUID = 'XXXX'O

        Click Yes if IUT received it, otherwise click No.

        Description: Verify
        that the Implementation Under Test (IUT) can send Discover all include
        services in database.
        """

        assert self.connection is not None
        assert self.services is not None
        """
        Number of checks can vary but information is always the same,
        so we need to iterate through the services and check if its included
        services match one of these.
        """
        all_matches = re.findall("'([a0-Z9]*)'O", description)
        found_services = 0
        for service in self.services:
            for i in range(0, len(all_matches), 4):
                if compareIncludedServices(service,\
                        (stringHandleToInt(all_matches[i])),\
                        stringHandleToInt(all_matches[i + 1]),\
                        formatUuid(all_matches[i + 3])):
                    found_services += 1
        assert found_services == (len(all_matches) / 4)
        return "OK"

    def MMI_IUT_DISCOVER_SERVICE_UUID(self, description: str, **kwargs):
        """
        Discover all characteristics of service UUID= 'XXXX'O,  Service start
        handle = 'XXXX'O, end handle = 'XXXX'O.

        Description: Verify that the
        Implementation Under Test (IUT) can send Discover all charactieristics
        of a service.
        """

        assert self.connection is not None
        service_uuid = formatUuid(re.findall("'([a0-Z9]*)'O", description)[0])
        self.services = self.gatt.DiscoverServices(connection=self.connection).services
        self.characteristics = getCharacteristicsForServiceUuid(self.services, service_uuid)
        return "OK"

    def MMI_CONFIRM_ALL_CHARACTERISTICS_SERVICE(self, description: str, **kwargs):
        """
        Please confirm IUT received all characteristics of service
        handle='XXXX'O handle='XXXX'O handle='XXXX'O handle='XXXX'O
        handle='XXXX'O handle='XXXX'O handle='XXXX'O handle='XXXX'O
        handle='XXXX'O handle='XXXX'O handle='XXXX'O  in database. Click Yes if
        IUT received it, otherwise click No.

        Description: Verify that the
        Implementation Under Test (IUT) can send Discover all characteristics of
        a service in database.
        """

        assert self.characteristics is not None
        all_matches = list(map(stringCharHandleToInt, re.findall("'([a0-Z9]*)'O", description)))
        assert all(handle in list(map(lambda char: char.handle, self.characteristics))\
                for handle in all_matches)
        return "Yes"

    def MMI_IUT_DISCOVER_SERVICE_UUID_RANGE(self, description: str, **kwargs):
        """
        Please send discover characteristics by UUID. Range start from handle =
        'XXXX'O end handle = 'XXXX'O characteristics UUID = 0xXXXX'O.
        Description: Verify that the Implementation Under Test (IUT) can send
        Discover characteristics by UUID.
        """

        assert self.connection is not None
        handles = re.findall("'([a0-Z9]*)'O", description)
        """
        PTS sends UUIDS description formatted differently in this MMI,
        so we need to check for each known format.
        """
        uuid_match = re.findall("0x([a0-Z9]*)'O", description)
        if len(uuid_match) == 0:
            uuid_match = re.search("UUID = (.*)'O", description)
            uuid = formatUuid(uuid_match[1])
        else:
            uuid = formatUuid(uuid_match[0])
        self.services = self.gatt.DiscoverServices(connection=self.connection).services
        self.characteristics = getCharacteristicsRange(self.services,\
                stringHandleToInt(handles[0]), stringHandleToInt(handles[1]), uuid)
        return "OK"

    def MMI_CONFIRM_CHARACTERISTICS(self, description: str, **kwargs):
        """
        Please confirm IUT received characteristic handle='XXXX'O UUID='XXXX'O
        in database. Click Yes if IUT received it, otherwise click No.
        Description: Verify that the Implementation Under Test (IUT) can send
        Discover primary service by UUID in database.
        """

        assert self.characteristics is not None
        all_matches = re.findall("'([a0-Z9-]*)'O", description)
        for characteristic in self.characteristics:
            if characteristic.handle == stringHandleToInt(all_matches[0])\
                    and characteristic.uuid == formatUuid(all_matches[1]):
                return "Yes"
        return "No"

    @assert_description
    def MMI_CONFIRM_NO_CHARACTERISTICSUUID_SMALL(self, **kwargs):
        """
        Please confirm that IUT received NO 128 bit uuid in the small database
        file. Click Yes if NO handle found, otherwise click No.

        Description:
        Verify that the Implementation Under Test (IUT) can discover
        characteristics by UUID in small database.
        """

        assert self.characteristics is not None
        assert len(self.characteristics) == 0
        return "OK"

    def MMI_IUT_DISCOVER_DESCRIPTOR_RANGE(self, description: str, **kwargs):
        """
        Please send discover characteristics descriptor range start from handle
        = 'XXXX'O end handle = 'XXXX'O to the PTS.

        Description: Verify that the
        Implementation Under Test (IUT) can send Discover characteristics
        descriptor.
        """

        assert self.connection is not None
        handles = re.findall("'([a0-Z9]*)'O", description)
        self.services = self.gatt.DiscoverServices(connection=self.connection).services
        self.descriptors = getDescriptorsRange(self.services,\
                stringHandleToInt(handles[0]), stringHandleToInt(handles[1]))
        return "OK"

    def MMI_CONFIRM_CHARACTERISTICS_DESCRIPTORS(self, description: str, **kwargs):
        """
        Please confirm IUT received characteristic descriptors handle='XXXX'O
        UUID=0xXXXX  in database. Click Yes if IUT received it, otherwise click
        No.

        Description: Verify that the Implementation Under Test (IUT) can
        send Discover characteristic descriptors in database.
        """

        assert self.descriptors is not None
        handle = stringHandleToInt(re.findall("'([a0-Z9]*)'O", description)[0])
        uuid = formatUuid(re.search("UUID=0x(.*)  ", description)[1])
        for descriptor in self.descriptors:
            if descriptor.handle == handle and descriptor.uuid == uuid:
                return "Yes"
        return "No"

    def MMI_IUT_DISCOVER_ALL_SERVICE_RECORD(self, pts_addr: bytes, description: str, **kwargs):
        """
        Please send Service Discovery to discover all primary Services. Click
        YES if GATT='XXXX'O services are discovered, otherwise click No.
        Description: Verify that the Implementation Under Test (IUT) can
        discover basic rate all primary services.
        """

        uuid = formatUuid(re.findall("'([a0-Z9]*)'O", description))
        self.services = self.gatt.DiscoverServicesSdp(address=pts_addr).service_uuids
        if uuid in self.services:
            return "Yes"
        return "No"


common_uuid = "0000XXXX-0000-1000-8000-00805f9b34fb"


def stringHandleToInt(handle: str):
    return int(handle, 16)


# Discovered characteristics handles are 1 more than PTS handles in one test.
def stringCharHandleToInt(handle: str):
    return (int(handle, 16) + 1)


def formatUuid(uuid: str):
    """
    Formats PTS described UUIDs to be of the right format.
    Right format is: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
    PTS described format can be:
    - 'XXXX'
    - 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    - 'XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX'
    """
    uuid_len = len(uuid)
    if uuid_len == 4:
        return common_uuid.replace(common_uuid[4:8], uuid.lower())
    elif uuid_len == 32 or uuid_len == 39:
        uuidCharList = list(uuid.replace('-', '').lower())
        uuidCharList.insert(20, '-')
        uuidCharList.insert(16, '-')
        uuidCharList.insert(12, '-')
        uuidCharList.insert(8, '-')
        return ''.join(uuidCharList)
    else:
        return uuid


def compareIncludedServices(service, service_handle, included_handle, included_uuid):
    """
    Compares included services with given values.
    The service_handle passed by the PTS is
    [primary service handle] + [included service number].
    """
    included_service_count = 1
    for included_service in service.included_services:
        if service.handle == (service_handle - included_service_count)\
                and included_service.handle == included_handle\
                and included_service.uuid == included_uuid:
            return True
        included_service_count += 1
    return False


def getCharacteristicsForServiceUuid(services, uuid):
    """
    Return an array of characteristics for matching service uuid.
    """
    for service in services:
        if service.uuid == uuid:
            return service.characteristics
    return []


def getCharacteristicsRange(services, start_handle, end_handle, uuid):
    """
    Return an array of characteristics of which handles are
    between start_handle and end_handle and uuid matches.
    """
    characteristics_list = []
    for service in services:
        for characteristic in service.characteristics:
            if characteristic.handle >= start_handle\
                    and characteristic.handle <= end_handle\
                    and characteristic.uuid == uuid:
                characteristics_list.append(characteristic)
    return characteristics_list


def getDescriptorsRange(services, start_handle, end_handle):
    """
    Return an array of descriptors of which handles are
    between start_handle and end_handle.
    """
    descriptors_list = []
    for service in services:
        for characteristic in service.characteristics:
            for descriptor in characteristic.descriptors:
                if descriptor.handle >= start_handle and descriptor.handle <= end_handle:
                    descriptors_list.append(descriptor)
    return descriptors_list