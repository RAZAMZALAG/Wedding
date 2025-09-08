# End-to-End (System) Tests

This directory contains comprehensive end-to-end tests that verify complete user workflows and system integration scenarios for the Wedding Planner application.

## Test Structure

### 1. User Workflows (`test_user_workflows.py`)
- **Complete User Journey**: Registration → Login → Browse → Book → Manage
- **Guest Browsing**: Unauthenticated user flows
- **Booking Modifications**: Update and manage existing bookings
- **AI Assistant Integration**: End-to-end AI interactions
- **Multi-User Scenarios**: Concurrent user operations
- **Error Handling**: Recovery from validation errors and authentication issues

### 2. System Integration (`test_system_integration.py`)
- **Catalog to Booking Integration**: Complete item selection to booking flow
- **Cross-Component Authentication**: Verify security across all endpoints
- **Data Consistency**: Ensure data integrity across operations
- **AI System Integration**: AI assistant interaction with other components
- **Database Resilience**: Test database operation reliability
- **API Availability**: Verify all endpoints are accessible

### 3. Business Scenarios (`test_business_scenarios.py`)
- **Wedding Planning Journey**: Complete wedding planning workflow
- **Corporate Events**: Business event planning scenarios
- **Multiple Events**: Users managing several events
- **Seasonal Scenarios**: Holiday rush and spring wedding season
- **Business Continuity**: Last-minute changes and peak usage

## Key Features Tested

### Authentication & Authorization
- User registration and login flows
- Token-based authentication across all protected endpoints
- Cross-user data isolation
- Session management and token validation

### Booking Workflows
- Complete booking creation process
- Item selection and integration
- Booking modifications and updates
- Multi-booking management per user

### System Integration
- Database transaction consistency
- Cross-component data flow
- API endpoint reliability
- Error handling and recovery

### Business Logic
- Real-world event planning scenarios
- Seasonal booking patterns
- Peak usage handling
- Concurrent user operations

## Test Configuration

Tests use dedicated fixtures in `conftest.py`:
- `e2e_app`: Full application instance for testing
- `e2e_client`: Test client for API requests
- `auth_headers`: Authenticated user headers
- `admin_headers`: Admin user headers
- `sample_booking_data`: Realistic booking data
- `sample_user_data`: User registration data

## Running E2E Tests

```bash
# Run all end-to-end tests
python -m pytest tests/e2e/ -v

# Run specific test categories
python -m pytest tests/e2e/test_user_workflows.py -v
python -m pytest tests/e2e/test_system_integration.py -v
python -m pytest tests/e2e/test_business_scenarios.py -v

# Run with detailed output
python -m pytest tests/e2e/ -v -s

# Run specific test
python -m pytest tests/e2e/test_user_workflows.py::TestCompleteUserJourney::test_user_registration_to_booking_workflow -v
```

## Test Scenarios Coverage

### User Experience Flows
- ✅ Guest browsing and exploration
- ✅ User registration and onboarding
- ✅ Authenticated user booking creation
- ✅ Booking management and modifications
- ✅ AI assistant consultation
- ✅ Multi-event planning

### System Reliability
- ✅ Database operation consistency
- ✅ Concurrent user handling
- ✅ Peak load simulation
- ✅ Error recovery mechanisms
- ✅ Authentication across components

### Business Scenarios
- ✅ Wedding planning workflows
- ✅ Corporate event management
- ✅ Seasonal booking patterns
- ✅ Last-minute changes
- ✅ Multi-user coordination

## Expected Outcomes

These tests verify that:
1. **Complete user workflows function end-to-end**
2. **System components integrate properly**
3. **Business requirements are met**
4. **Data integrity is maintained**
5. **Security is enforced throughout**
6. **System handles real-world usage patterns**

## Test Data Management

Tests create isolated test data that doesn't interfere with other test categories. Each test class uses unique user emails and booking identifiers to prevent conflicts.

## Performance Considerations

E2E tests are designed to be comprehensive but efficient:
- Sequential execution to avoid resource conflicts
- Realistic but minimal data sets
- Focused assertions on critical functionality
- Graceful handling of rate limits and quotas
