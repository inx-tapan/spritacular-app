import pytz

TIME_ZONES = pytz.all_timezones

# Validation Messages
FIELD_REQUIRED = '{} field may not be blank.'
SINGLE_IMAGE_VALID = 'Number of the images should not be more than 1.'
MULTIPLE_IMAGE_VALID = 'Number of the images should not be more than 3.'

# Response Messages
NOT_FOUND = {'detail': 'Not found.', 'status': 0}
OBS_FORM_SUCCESS = {'success': 'Form submitted successfully', 'status': 1}

SOMETHING_WENT_WRONG = {'details': 'Something went wrong.', 'status': 0}
