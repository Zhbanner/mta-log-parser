from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
# TODO dayjs? as moment is deprecated
import moment
from typing import List

from dateutil.parser import parse
from privex.helpers import Dictable, is_false

from mlp.settings import log_timezone
from mlp import settings, api

import logging
log = logging.getLogger(__name__)

@dataclass
class PostfixLog(Dictable):
    timestamp: datetime
    queue_id: str
    message: str

    def __post_init__(self):
        if type(self.timestamp) is not datetime:
            self.timestamp = log_timezone.localize(parse(self.timestamp))
        #if type(self.message) is list:
        #    self.message[]
        self.message = self.message.strip()
        self.queue_id = self.queue_id.strip()

    def __repr__(self):
        return f'<PostfixLog timestamp="{self.timestamp}" queue_id="{self.queue_id}" message="{self.message}" />'

    def __str__(self):
        return self.__repr__()

    # Make date one year lower. Fix for postfix log date format
    def year_minus(self):
        self.timestamp = self.timestamp.replace(year=self.timestamp.year-1)

    def clean_dict(self, convert_time=str) -> dict:
        data = dict(self)
        # log lines timestamp convert before append (for message related log view)
        # this data conversion uses only one thread and takes too long so do it according to mail_log_timestamp_convert variable value
        # log.info('Converting date and time %s using moment library according to settings',  data['timestamp'])
        if settings.mail_log_timestamp_convert:
            data['timestamp'] = moment.date(str(self.timestamp)).format(settings.datetime_format)
        else:
        #print(data)

            if is_false(convert_time):
                data['timestamp'] = self.timestamp
            else:
                data['timestamp'] = convert_time(self.timestamp)

        return data

@dataclass
class PostfixMessage(Dictable):
    timestamp: datetime
    queue_id: str
    lines: List[PostfixLog] = field(default_factory=list)
    mail_to: str = ""
    mail_to_alias: dict = field(default_factory=dict)
    #mail_to_alias: str = ""
    #mail_to: dict = field(default_factory=dict)
    mail_from: str = ""
    subject: str = ""
    size: float  = 0
    message_id: str = ""
    status: dict = field(default_factory=dict)
    relay: dict = field(default_factory=dict)
    client: dict = field(default_factory=dict)

    def __post_init__(self):
        if type(self.timestamp) is not datetime:
            self.timestamp = log_timezone.localize(parse(self.timestamp))
        self.queue_id = self.queue_id.strip()

    def __repr__(self):
        return f'<PostfixMessage timestamp="{self.timestamp}" queue_id="{self.queue_id}" status="{self.status}" />'

    def __str__(self):
        return self.__repr__()

    @property
    def first_attempt(self) -> datetime:
        return self.lines[0].timestamp

    @property
    def last_attempt(self) -> datetime:
        return self.lines[-1].timestamp

    def merge(self, dicdata: dict):
        for k, v in dicdata.items():
            if hasattr(self, k):
                setattr(self, k, v)

    # Make date one year lower. Fix for postfix log date format
    def year_minus(self):
        self.timestamp = self.timestamp.replace(year=self.timestamp.year-1)
        for line in self.lines:
            line.year_minus()

    def clean_dict(self, convert_time=str) -> dict:
        data = dict(self)
        #print(data)
        if is_false(convert_time):
            data['timestamp'] = self.timestamp
            data['first_attempt'], data['last_attempt'] = self.first_attempt, self.last_attempt
        else:
            data['timestamp'] = convert_time(self.timestamp)
            data['first_attempt'] = convert_time(self.first_attempt)
            data['last_attempt'] = convert_time(self.last_attempt)
        
        data['lines'] = [s.clean_dict(convert_time=convert_time) for s in self.lines]
        
        return data
