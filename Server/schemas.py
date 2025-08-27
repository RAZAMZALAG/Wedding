from marshmallow import fields, Schema
from logger_config import get_logger

# Setup logger for schema operations
logger = get_logger(__name__)


class UserSchema(Schema):
    id = fields.String()
    email = fields.String()
    first_name = fields.String()
    last_name = fields.String()


class BytesField(fields.Field):
    """Custom field to handle binary data (BYTEA) in Marshmallow schemas."""

    def _validate(self, value):
        """Validate that the input is of type bytes."""
        if not isinstance(value, bytes):
            raise ValidationError("Invalid input type. Expected bytes.")

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize the binary data to a base64-encoded string."""
        if value is None:
            return None
        return value.decode("utf-8")  # Assuming UTF-8 encoding; adjust as needed

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize the base64-encoded string back to binary data."""
        if value is None:
            return None
        return value.encode("utf-8")  # Adjust encoding as needed


import base64
from marshmallow import ValidationError


class Base64BytesField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        if not isinstance(value, (str, bytes, bytearray)):
            logger.warning("Invalid data type for Base64 serialization", extra={
                "expected_type": "bytes/str",
                "actual_type": type(value).__name__,
                "field_name": attr
            })
            raise ValidationError('Expected bytes for Base64BytesField')
        return base64.b64encode(value).decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        if not isinstance(value, str):
            logger.warning("Invalid data type for Base64 deserialization", extra={
                "expected_type": "str",
                "actual_type": type(value).__name__,
                "field_name": attr
            })
            raise ValidationError('Expected string for Base64BytesField')
        try:
            return base64.b64decode(value)
        except Exception as e:
            logger.error("Base64 decoding failed", extra={
                "field_name": attr,
                "value_length": len(value) if isinstance(value, str) else 0
            }, exc_info=True)
            raise ValidationError('Invalid base64 string') from e


class UserIdFileSchema(Schema):
    id_file = Base64BytesField()


class ManagedUserSchema(Schema):
    id = fields.String()
    email = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    phone_number = fields.String()
    location = fields.String()
    blocked = fields.Bool()
    permission = fields.Number()
    verified = fields.Bool()


class ItemSchema(Schema):
    id = fields.String()
    name = fields.String()
    category = fields.String()
    total_amount = fields.Integer()
    amount = fields.Integer()
    price = fields.Float()
    notes = fields.String()
    description = fields.String()
    condition = fields.String()
    image = fields.Raw()
    hidden = fields.Bool()


class CategorySchema(Schema):
    name = fields.String()


class CartSchema(Schema):
    id = fields.String()
    user_id = fields.Str(required=True)
    status = fields.Str(required=True)


class BookingSchema(Schema):
    # The cart_id instead of item_id since order is related to a cart now
    cart_id = fields.Str(required=True)

    # Dates and pricing information for rental orders
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    submission_date = fields.Date(required=True)
    total_price = fields.Int(required=True)
    status = fields.Str(required=True)
    customer_notes = fields.Str(allow_none=True)

    # Add the finalization_date to the schema
    finalization_date = fields.Date(allow_none=True)

    # Nested schemas
    user = fields.Nested(UserSchema, required=True)
    cart = fields.Nested(CartSchema, required=True)  # Including cart details in the order response


# Alias for backward compatibility
OrderSchema = BookingSchema
