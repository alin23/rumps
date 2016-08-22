_NOTIFICATIONS = True
try:
    from Foundation import NSUserNotification, NSUserNotificationCenter, NSDate, NSDateComponents
except ImportError:
    _NOTIFICATIONS = False
from collections import Mapping
from PyObjCTools import KeyValueCoding as kvc

def _require_string_or_none(*objs):
    for obj in objs:
        if not(obj is None or isinstance(obj, basestring)):
            raise TypeError('a string or None is required but given {0}, a {1}'.format(obj, type(obj).__name__))


class RumpsNotifier(object):
    """RUMPS Notifier"""

    def __init__(self):
        super(RumpsNotifier, self).__init__()
        if _NOTIFICATIONS:
            self.defaultNotificationCenter = NSUserNotificationCenter.defaultUserNotificationCenter()

    @property
    def scheduledNotifications(self):
        return self.defaultNotificationCenter.scheduledNotifications

    def removeScheduledNotification(self, notification):
        self.defaultNotificationCenter.removeScheduledNotification_(notification)

    def removeAllScheduledNotifications(self):
        self.defaultNotificationCenter.setScheduledNotifications_([])

    def removeDeliveredNotification(self, notification):
        self.defaultNotificationCenter.removeDeliveredNotification_(notification)

    def removeAllDeliveredNotifications(self):
        self.defaultNotificationCenter.removeAllDeliveredNotifications()

    def notifications(self, f):
        """Decorator for registering a function to serve as a "notification center" for the application. This function will
        receive the data associated with an incoming OS X notification sent using :func:`rumps.notification`. This occurs
        whenever the user clicks on a notification for this application in the OS X Notification Center.

        .. code-block:: python

            @Notifier.notifications
            def notification_center(info):
                if 'unix' in info:
                    print 'i know this'

        """
        self.__dict__['*notification_center'] = f
        return f

    def notify(self,
               title='', subtitle='', message='', data=None,
               sound='NSUserNotificationDefaultSoundName',
               after=0, repeat={}):
        """Send a notification to Notification Center (Mac OS X 10.8+). If running on a version of Mac OS X that does not
        support notifications, a ``RuntimeError`` will be raised. Apple says,

            "The userInfo content must be of reasonable serialized size (less than 1k) or an exception will be thrown."

        So don't do that!

        :param title: text in a larger font.
        :param subtitle: text in a smaller font below the `title`.
        :param message: text representing the body of the notification below the `subtitle`.
        :param data: will be passed to the application's "notification center" (see :func:`rumps.notifications`) when this
                     notification is clicked.
        :param sound: whether the notification should make a noise when it arrives.
        :param after: number of seconds to postpone the notification.
        :param repeat: dict of date components that specify how the notification shoul be repeated.
                       e.g. {'hour': 1, 'minute': 30}
        """
        after = max(after, 0)

        if not _NOTIFICATIONS:
            raise RuntimeError('Mac OS X 10.8+ is required to send notifications')
        if data is not None and not isinstance(data, Mapping):
            raise TypeError('notification data must be a mapping')

        _require_string_or_none(title, subtitle, message, sound)
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setSubtitle_(subtitle)
        notification.setInformativeText_(message)
        notification.setUserInfo_(data or {})

        if sound:
            notification.setSoundName_(sound)

        if after:
            notification.setDeliveryDate_(NSDate.dateWithTimeIntervalSinceNow_(after))
        if repeat:
            deliveryRepeatInterval = NSDateComponents.alloc().init()
            for k, v in repeat.items():
                kvc.setKey(deliveryRepeatInterval, k, v)
            notification.setDeliveryRepeatInterval_(deliveryRepeatInterval)

        self.defaultNotificationCenter.scheduleNotification_(notification)

        return notification
