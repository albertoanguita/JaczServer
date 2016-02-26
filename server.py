#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime
import logging
import endpoints
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb

from models import HelloReturn
from models import RegistrationRequest
from models import RegistrationResponse
from models import RegistrationResponseValue
from models import ConnectionRequest
from models import ConnectionResponse
from models import ConnectionResponseValue
from models import UpdateRequest
from models import RefreshResponse
from models import RefreshResponseValue
from models import DisconnectResponse
from models import InfoRequest
from models import PeerIDInfo
from models import InfoResponse
from models import PeerData
from models import ActiveSession
from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE
import urllib
from google.appengine.api import urlfetch

API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

MIN_REMINDER_TIME = 18 * 60000
MAX_REMINDER_TIME = 20 * 60000



@endpoints.api(name='server', version='v1', audiences=[ANDROID_AUDIENCE],
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID,
                                   ANDROID_CLIENT_ID, IOS_CLIENT_ID],
               scopes=[])
class ServerApi(remote.Service):

    @endpoints.method(message_types.VoidMessage, HelloReturn, path='hello',
                      http_method='GET', name='hello')
    def hello(self, request):
        """Create new conference."""
        response = HelloReturn()
        setattr(response, "response", "hello alb")
        return response

    @endpoints.method(RegistrationRequest, RegistrationResponse,
                      path='register',
                      http_method='POST', name='register')
    def register(self, request):
        # check that this peer has not been already registered
        existing_peer_data = self._get_peer_data(request.peerID)
        if existing_peer_data:
            # peer is already registered
            return RegistrationResponse(response=RegistrationResponseValue.ALREADY_REGISTERED)

        now = datetime.datetime.now()
        peer_data = PeerData(peerID=request.peerID,
                             registrationTime=now,
                             publicKeySizes=request.publicKeySizes,
                             publicKeyValues=request.publicKeyValues)
        peer_data.put()
        return RegistrationResponse(response=RegistrationResponseValue.OK)

    @endpoints.method(ConnectionRequest, ConnectionResponse, path='connect',
                      http_method='POST', name='connect')
    def connect(self, request):
        """Create new conference."""
        # session_id = generate_session_id(32)
        # check fields from request
        if not request.peerID:
            raise endpoints.BadRequestException(
                "Request 'peerID' field required")

        if not request.localIPAddress:
            raise endpoints.BadRequestException(
                "Request 'localIPAddress' field required")

        if not request.localMainServerPort:
            raise endpoints.BadRequestException(
                "Request 'localMainServerPort' field required")

        # if not request.localRESTServerPort:
        #     raise endpoints.BadRequestException(
        #         "Request 'localRESTServerPort' field required")

        if not request.externalMainServerPort:
            raise endpoints.BadRequestException(
                "Request 'externalMainServerPort' field required")

        # if not request.externalRESTServerPort:
        #     raise endpoints.BadRequestException(
        #         "Request 'externalRESTServerPort' field required")

        existing_peer_data = self._get_peer_data(request.peerID)
        if not existing_peer_data:
            # peer is not registered
            return ConnectionResponse(response=ConnectionResponseValue.UNREGISTERED_PEER)

        # self.test_peer_ports(
        #     request.peerID,
        #     request.localIPAddress,
        #     request.externalMainServerPort)

        existing_session = self._get_active_session_by_peer(peer_id=request.peerID)
        if existing_session:
            logging.info("Session already exists, deleting old session")
            existing_session.key.delete()

        # create new session
        now = datetime.datetime.now()
        active_session = ActiveSession(peerID=request.peerID,
                                       connectionTime=now,
                                       lastRefreshTime=now,
                                       localIPAddress=request.localIPAddress,
                                       externalIPAddress=self.request_state.remote_address,
                                       localMainServerPort=request.localMainServerPort,
                                       # localRESTServerPort=request.localRESTServerPort,
                                       externalMainServerPort=request.externalMainServerPort)
                                       # externalRESTServerPort=request.externalRESTServerPort)
        active_session_key = active_session.put()
        session_id = active_session_key.urlsafe()

        # generate the response
        connection_response = ConnectionResponse(response=ConnectionResponseValue.OK,
                                                 sessionID=session_id,
                                                 minReminderTime=MIN_REMINDER_TIME,
                                                 maxReminderTime=MAX_REMINDER_TIME)
        # response = ConnectionResponse()
        # setattr(response, "response", "hello, %s" % request.peerID)
        # setattr(response, "verb", "POST")
        return connection_response

    @endpoints.method(UpdateRequest, RefreshResponse, path='refresh',
                      http_method='POST', name='refresh')
    def refresh(self, request):
        """Create new conference."""
        # session_id = generate_session_id(32)
        # check fields from request
        if not request.sessionID:
            raise endpoints.BadRequestException(
                "Request 'sessionID' field required")

        active_session = self._get_active_session_by_key(request.sessionID)
        if active_session:
            # active session for this peer exists
            # check that the peer IP address is similar to the stored one
            if (active_session.externalIPAddress != self.request_state.remote_address):
                return RefreshResponse(response=RefreshResponseValue.WRONG_IP_ADDRESS)
            # Check if ok or too soon
            now = datetime.datetime.now()
            if active_session.lastRefreshTime < now - datetime.timedelta(milliseconds=MIN_REMINDER_TIME):
                # last refresh time older than now - MIN_REMINDER_TIME -> OK
                active_session.lastRefreshTime = now
                active_session.put()
                return RefreshResponse(response=RefreshResponseValue.OK)
            else:
                # too soon, remove active_session and notify
                active_session.key.delete()
                return RefreshResponse(response=RefreshResponseValue.TOO_SOON)

        else:
            return RefreshResponse(response=RefreshResponseValue.UNRECOGNIZED_SESSION)

    @endpoints.method(UpdateRequest, DisconnectResponse, path='disconnect',
                      http_method='POST', name='disconnect')
    def disconnect(self, request):
        """Create new conference."""
        # session_id = generate_session_id(32)
        # check fields from request
        if not request.sessionID:
            raise endpoints.BadRequestException(
                "Request 'sessionID' field required")

        active_session = self._get_active_session_by_key(request.sessionID)
        if active_session:
            active_session.key.delete()
            return DisconnectResponse(response="OK")
        else:
            return DisconnectResponse(response="UNRECOGNIZED_SESSION")

    @endpoints.method(InfoRequest, InfoResponse, path='info',
                      http_method='POST', name='info')
    def info(self, request):
        """Create new conference."""
        # session_id = generate_session_id(32)
        # check fields from request
        if not request.peerIDList:
            raise endpoints.BadRequestException(
                "Request 'peerIDList' field required")

        # copy peerIDs in a list
        peer_id_list = []
        for peerID in request.peerIDList:
            peer_id_list.append(peerID)

        active_sessions = ActiveSession\
            .query(ActiveSession.peerID.IN(peer_id_list))\
            .fetch()

        peer_id_info_list = []
        for peer_session in active_sessions:
            peer_id_info_list.append(
                PeerIDInfo(
                    peerID=peer_session.peerID,
                    localIPAddress=peer_session.localIPAddress,
                    externalIPAddress=peer_session.externalIPAddress,
                    localMainServerPort=peer_session.localMainServerPort,
                    externalMainServerPort=peer_session.externalMainServerPort
                )
            )

        info_response = InfoResponse(peerIDInfoList=peer_id_info_list)
        return info_response

    @staticmethod
    def _get_peer_data(peer_id):
        return PeerData.query(PeerData.peerID == peer_id).get()

    def _get_active_session_by_key(self, session_id):
        try:
            session_key = ndb.Key(urlsafe=session_id)
            active_session = session_key.get()
            if active_session:
                return active_session
            else:
                return None
        except Exception:
            return None

    def _get_active_session_by_peer(
            self,
            peer_id):
        return ActiveSession.query(ActiveSession.peerID == peer_id).get()

    def test_peer_ports(
            self,
            peer_id,
            public_ip,
            main_port):
        # generate POST request for the ports test server
        form_fields = {
            "ip": public_ip,
            "port": main_port,
            "peerid": peer_id
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(
            url="http://159.147.253.223:8080/porttestservice/ports",
            # url="http://127.0.0.1:8080/porttestservice/ports",
            payload=form_data,
            method=urlfetch.POST,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'})
        logging.info(result.content)
        return

    @staticmethod
    def _remove_old_clients():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        limit = datetime.datetime.now() - \
                datetime.timedelta(milliseconds=MAX_REMINDER_TIME)
        logging.info("Deleting sessions older than " + unicode(limit))
        # recover all sessions with lastRefreshTime older than limit
        old_sessions = ActiveSession.query(
            ActiveSession.lastRefreshTime < limit).fetch()
        for old_session in old_sessions:
            # delete old session
            logging.info("Deleting session " + old_session.peerID)
            old_session.key.delete()

        return


api = endpoints.api_server([ServerApi])  # register API
