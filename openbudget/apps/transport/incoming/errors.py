from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _


class DataInputError(object):

    def __init__(self, row=None, columns=None, values=None):
        if row is None:
            row = 'Unknown'
        self.row = row
        self.columns = columns or ['Unknown']
        self.values = values or ['Unknown']

    def __dict__(self):
        return {
            'row': self.row,
            'columns': self.columns,
            'values': self.values,
            'message': self.message
        }

    @property
    def _message(self):
        return _('Error found in row: %s; and columns: %s; with values: %s')

    @property
    def message(self):
        return self._message % (self.row, ', '.join(self.columns), ', '.join(self.values))


class DataCollisionError(object):

    def __init__(self, rows=None):
        self.rows = rows or ['Unknown', 'Unknown']

    def __dict__(self):
        return {
            'rows': self.rows,
            'message': self.message
        }

    @property
    def _message(self):
        return _('Source data collision error in rows: %s, %s')

    @property
    def message(self):
        return self._message % self.rows


class DataSyntaxError(DataInputError):

    def __unicode__(self):
        return _('Data Syntax Error')

    @property
    def _message(self):
        return _('Syntax error found in row: %s; and columns: %s; with values: %s')


class DataAmbiguityError(DataCollisionError):

    def __unicode__(self):
        return _('Data Ambiguity Error')

    @property
    def _message(self):
        return _('Source contains siblings with same code in rows: %s, %s')


class MetaParsingError(object):

    def __init__(self, reason='Unknown'):
        self.reason = reason

    def __dict__(self):
        return {
            'reason': self.reason,
            'message': self.message
        }

    def __unicode__(self):
        return _('Meta Parsing Error')

    @property
    def message(self):
        return _('Source meta data invalid for reason: %s') % self.reason


class DataValidationError(DataInputError):

    def __init__(self, reasons=None, row='Unknown'):
        super(DataValidationError, self).__init__(row=row)
        self.reasons = reasons

    def __dict__(self):
        error_dic = super(DataValidationError, self).__dict__()
        error_dic['reasons'] = self.reasons
        return error_dic

    def __unicode__(self):
        return _('Data Validation Error')

    @property
    def message(self):
        reasons = 'Unknown'

        if self.reasons:
            reasons = []
            for key, messages in self.reasons.iteritems():
                if key == NON_FIELD_ERRORS:
                    key = 'others'

                reasons.append('%s: %s' % (key, 'and '.join(messages)))

            reasons = ' AND '.join(reasons)

        return _('Source data invalid in row: %s; for reasons: %s') % (self.row, reasons)


class NodeDirectionError(DataCollisionError):

    def __unicode__(self):
        return _('Node Direction Error')

    @property
    def _message(self):
        return _("Inverse node's direction is not opposite of item in row: %s; and inverse in row: %s")


class ParentScopeError(DataInputError):

    def __unicode__(self):
        return _('Parent Scope Error')

    @property
    def _message(self):
        return _("Parent scope is missing or not resolvable in row: %s")

    @property
    def message(self):
        return self._message % self.row


class NodeNotFoundError(DataInputError):

    @property
    def _message(self):
        return _('Budget template node not found for item in row: %s; and columns: %s; with values: %s')


class ParentNodeNotFoundError(DataInputError):

    @property
    def _message(self):
        return _('Parent node not found for item in row: %s; and columns: %s; with values: %s')


class PathInterpolationError(DataInputError):

    def __unicode__(self):
        return _('Nodes Path Interpolation Error')

    @property
    def _message(self):
        return _('Interpolation failed, no ancestor found for row: %s')
