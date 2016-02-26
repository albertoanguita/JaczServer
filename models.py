from protorpc import messages
from google.appengine.ext import ndb


class HelloReturn(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    response = messages.StringField(1)


class RegistrationRequest(messages.Message):
    # peer ID of the requesting peer
    peerID          = messages.StringField(1)
    publicKeySizes  = messages.IntegerField(2, repeated=True)
    # hexadecimal
    publicKeyValues = messages.StringField(3, repeated=True)
    # public key for encryption --> FOR THE FUTURE
    # publicKey = messages.IntegerField(4)


class RegistrationResponse(messages.Message):
    # registration response
    # todo INVALID_REGISTRATION_VALUE
    response = messages.StringField(1)


class RegistrationResponseValue:
    OK = 'OK'
    INVALID_REGISTRATION_VALUE = 'INVALID_REGISTRATION_VALUE'
    ALREADY_REGISTERED = 'ALREADY_REGISTERED'


class ConnectionRequest(messages.Message):
    # peer ID of the requesting peer
    peerID = messages.StringField(1)
    # local IP address of the peer, of the type "192.168.1.10"
    localIPAddress = messages.StringField(2)
    #
    localMainServerPort = messages.IntegerField(3)
    localRESTServerPort = messages.IntegerField(4)
    # external port that the peer offers to other peers for connecting to him
    # between 0 and 65535
    externalMainServerPort = messages.IntegerField(5)
    externalRESTServerPort = messages.IntegerField(6)
    clientCountryCode = messages.StringField(7)


class ConnectionResponse(messages.Message):
    # result of the request:
    # OK -> connection accepted, sessionID contains the session identifier
    # UNREGISTERED_PEER -> this peer is not registered. Registration is
    # required prior to connection
    # PEER_MAIN_SERVER_UNREACHABLE -> the server is unable to successfully
    # test the user connection
    # PEER_REST_SERVER_UNREACHABLE -> the server is unable to
    # successfully establish connection with the peer REST server
    # WRONG_AUTHENTICATION -> the authentication process did not end
    # successfully
    response = messages.StringField(1)
    # unique session ID. If the connection was accepted, this field contains
    # the session ID
    sessionID = messages.StringField(2)
    # these fields indicate the times that the peer must use for refreshing
    # his connection with the server. The refreshing message must be produced
    # later than mixReminderTime and earlier than maxReminderTime. If it is
    # too soon, the client will be disconnected. If the maxReminderTime is
    # reached, the server will consider the client as disconnected, and
    # clear his session
    minReminderTime = messages.IntegerField(3)
    maxReminderTime = messages.IntegerField(4)


class ConnectionResponseValue:
    OK = 'OK'
    UNREGISTERED_PEER = 'UNREGISTERED_PEER'
    PEER_MAIN_SERVER_UNREACHABLE = 'PEER_MAIN_SERVER_UNREACHABLE'
    PEER_REST_SERVER_UNREACHABLE = 'PEER_REST_SERVER_UNREACHABLE'
    WRONG_AUTHENTICATION = 'WRONG_AUTHENTICATION'


class UpdateRequest(messages.Message):
    # session ID to update (either refresh or disconnect)
    sessionID = messages.StringField(1)


class RefreshResponse(messages.Message):
    # OK
    # UNRECOGNIZED_SESSION
    # todo TOO_SOON (for refresh only. Session is disconnected and requires peer
    # connecting again)
    response = messages.StringField(1)


class RefreshResponseValue:
    OK = 'OK'
    TOO_SOON = 'TOO_SOON'
    UNRECOGNIZED_SESSION = 'UNRECOGNIZED_SESSION'
    WRONG_IP_ADDRESS = 'WRONG_IP_ADDRESS'


class DisconnectResponse(messages.Message):
    # OK
    # UNRECOGNIZED_SESSION
    # connecting again)
    response = messages.StringField(1)


class DisconnectResponseValue:
    OK = 'OK'
    UNRECOGNIZED_SESSION = 'UNRECOGNIZED_SESSION'


class InfoRequest(messages.Message):
    peerIDList = messages.StringField(1, repeated=True)


class PeerIDInfo(messages.Message):
    peerID = messages.StringField(1)
    localIPAddress = messages.StringField(2)
    externalIPAddress = messages.StringField(3)
    localMainServerPort = messages.IntegerField(4)
    localRESTServerPort = messages.IntegerField(5)
    # external port that the peer offers to other peers for connecting to him
    # between 0 and 65535
    externalMainServerPort = messages.IntegerField(6)
    externalRESTServerPort = messages.IntegerField(7)


class InfoResponse(messages.Message):
    peerIDInfoList = messages.MessageField(PeerIDInfo, 1, repeated=True)


class PeerData(ndb.Model):
    """Conference -- Conference object"""
    # sessionID              = ndb.StringProperty(required=True)
    peerID           = ndb.StringProperty(required=True, indexed=True)
    registrationTime = ndb.DateTimeProperty(required=True, indexed=False)
    publicKeySizes   = ndb.IntegerProperty(indexed=False, repeated=True)
    # hexadecimal
    publicKeyValues  = ndb.StringProperty(indexed=False, repeated=True)


class ActiveSession(ndb.Model):
    """Conference -- Conference object"""
    # sessionID              = ndb.StringProperty(required=True)
    peerID                 = ndb.StringProperty(required=True)
    connectionTime         = ndb.DateTimeProperty(required=True, indexed=False)
    lastRefreshTime        = ndb.DateTimeProperty(required=True)
    localIPAddress         = ndb.StringProperty(required=True, indexed=False)
    externalIPAddress      = ndb.StringProperty(required=True, indexed=False)
    localMainServerPort    = ndb.IntegerProperty(required=True, indexed=False)
    localRESTServerPort    = ndb.IntegerProperty(required=False, indexed=False)
    externalMainServerPort = ndb.IntegerProperty(required=True, indexed=False)
    externalRESTServerPort = ndb.IntegerProperty(required=False, indexed=False)
    clientCountryCode      = ndb.StringProperty(required=False, indexed=False)


# class StoredSession(ndb.Model):
#     """Conference -- Conference object"""
#     connectionTime    = ndb.DateProperty(required=True)
#     disconnectionTime = ndb.DateProperty(required=True)
#     countryCode       = ndb.StringProperty()
