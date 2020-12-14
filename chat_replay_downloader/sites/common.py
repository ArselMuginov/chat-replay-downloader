
import requests
from http.cookiejar import MozillaCookieJar, LoadError
import os
from ..errors import (
    CookieError,
    ParsingError,
    JSONParseError,
    CallbackFunction
    )

from ..utils import (
    get_title_of_webpage,
    update_dict_without_overwrite
    )


from json import JSONDecodeError

class ChatDownloader:
    """
    Subclasses of this one should re-define the get_chat_messages()
    method and define a _VALID_URL regexp.

    Each chat item is a dictionary and must contain the following fields:

    message:                Actual content/text of the chat item
    timestamp:              UNIX time (in microseconds) of when the message was sent
    id:                     Identifier for the chat item
    author_id:              Idenfifier for the person who sent the message
    author_name:            Name of the user which sent the message


    If the stream is not live (e.g. is a replay/vod/clip), it must contain the following fields:

    time_in_seconds:        The number of seconds after the video began, that the message was sent
    time_text:              Human-readable format for `time_in_seconds`



    The following fields are optional:

    author_display_name:    The name of the author which is displayed to the viewer.
                            This value may be different to `author_name`

    TODO
    """

    # id
	# author_id
	# author_name
	# amount
	# message
	# time_text
	# timestamp
	# author_images
	# tooltip
	# icon
	# author_badges
	# badge_icons
	# sticker_images
	# ticker_duration
	# sponsor_icons
	# ticker_icons

	# target_id
	# action
	# viewer_is_creator
	# sub_message

    _DEFAULT_INIT_PARAMS = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Accept-Language': 'en-US, en'
        },

        'cookies': None # cookies file (optional)
    }
    _INIT_PARAMS = _DEFAULT_INIT_PARAMS

    _DEFAULT_PARAMS = {
        'url': None, # should be overridden
        'messages': [], # list of messages to append to
        'start_time': None, # get from beginning (even before stream starts)
        'end_time':None, # get until end
        'callback':None, # do something for every message

        'max_attempts': 30,
        # TODO timeout between attempts
        'max_messages': None,

        'output': None,
        'logging': 'normal',
        'safe_print': False,

        'timeout': None, # stop getting messages after no messages have been sent for `timeout` seconds



        'message_types': ['messages'], #,'superchat'

        # YouTube only
        'chat_type': 'live', # live or top


        # Twitch only

        # allows for keyboard interrupts to occur
        'message_receive_timeout': 0.1, #0.25, # try again after receiving no data after a certain time
        'buffer_size': 4096 # default buffer size for socket
    }

    def __str__(self):
        return ''

    @staticmethod
    def get_param_value(params, key):
        return params.get(key, ChatDownloader._DEFAULT_PARAMS.get(key))

    @staticmethod
    def remap(info, remapping_dict, remapping_functions, remap_key, remap_input):
        remap = remapping_dict.get(remap_key)

        if(remap):
            if(isinstance(remap, tuple)):
                index, mapping_function = remap
                info[index] = remapping_functions[mapping_function](remap_input)
            else:
                info[remap] = remap_input
        # else:
        #     pass # do nothing

    def __init__(self, updated_init_params = {}):
        """Initialise a new session for making requests."""
        # self._name = None
        self._INIT_PARAMS.update(updated_init_params)

        self.session = requests.Session()
        self.session.headers = self._INIT_PARAMS.get('headers')

        cookies = self._INIT_PARAMS.get('cookies')
        cj = MozillaCookieJar(cookies)

        if cookies: #  is not None
            # Only attempt to load if the cookie file exists.
            if os.path.exists(cookies):
                cj.load(ignore_discard=True, ignore_expires=True)
            else:
                raise CookieError(
                    'The file "{}" could not be found.'.format(cookies))
        self.session.cookies = cj

    def close(self):
        self.session.close()


    def _session_post(self, url, data = {}, headers={}):
        """Make a request using the current session."""
        #print('_session_post', url, data, headers)

        #update_dict_without_overwrite
        new_headers = {**self.session.headers, **headers}
        return self.session.post(url, data=data, headers=new_headers).json()

    def _session_get(self, url):
        """Make a request using the current session."""
        return self.session.get(url)

    def _session_get_json(self, url):
        """Make a request using the current session and get json data."""
        s = self._session_get(url)

        try:
            return s.json()
        except JSONDecodeError:
            #print(s.text)
            webpage_title = get_title_of_webpage(s.text)
            raise JSONParseError(webpage_title)

    _VALID_URL = None
    _CALLBACK = None

    #_LIST_OF_MESSAGES = []
    def get_chat_messages(self, params = {}):
    #def get_chat_messages(self, url, list_of_messages = []):
        """
        Returns a list of chat messages. To be redefined in subclasses.

        `params` should update its `messages` atttribute to allow for messages to still be
        returned after an exception is raised.
        """

        update_dict_without_overwrite(params, self._DEFAULT_PARAMS)
        # temp = params.copy()
        # params.update()
        # params.update(temp)
        #self._PARAMS.update()
        #params.update(self._PARAMS)

    def get_tests(self):
        t = getattr(self, '_TEST', None)
        if t:
            assert not hasattr(self, '_TESTS'), \
                '%s has _TEST and _TESTS' % type(self).__name__
            tests = [t]
        else:
            tests = getattr(self, '_TESTS', [])
        for t in tests:
            yield t

    @staticmethod
    def perform_callback(callback, data):
        try:
            callback(data)
        except TypeError:
            raise CallbackFunction(
                'Incorrect number of parameters for function '+callback.__name__)
    # _LOGGING_TYPES = {
    #     'errors'
    # }