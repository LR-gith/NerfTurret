import pytest

from turret.pi_controller import PiController


@pytest.fixture
def gpio_mock_on_pi(mocker):
    gpio_mock = mocker.patch('turret.pi_controller.GPIO')
    mocker.patch('turret.pi_controller.running_on_pi', True)
    return gpio_mock


@pytest.fixture
def gpio_mock_not_on_pi(mocker):
    gpio_mock = mocker.patch('turret.pi_controller.GPIO')
    mocker.patch('turret.pi_controller.running_on_pi', False)
    return gpio_mock


@pytest.fixture
def time_mock(mocker):
    return mocker.patch('turret.pi_controller.time')


@pytest.fixture
def controller():
    return PiController(1, 2, 3, 4)


def test_init_pin_assign(gpio_mock_on_pi, controller):
    assert controller.x_servo_pin == 1
    assert controller.load_pin == 4


def test_init_on_pi(gpio_mock_on_pi, controller):
    assert gpio_mock_on_pi.setup.call_count == 4
    assert gpio_mock_on_pi.setmode.call_count == 1


def test_init_not_on_pi(gpio_mock_not_on_pi):
    assert gpio_mock_not_on_pi.setup.call_count == 0
    assert gpio_mock_not_on_pi.setmode.call_count == 0


def test_shoot_invalid_sleep_times(gpio_mock_on_pi, controller):
    with pytest.raises(ValueError):
        controller.shoot(0, -3)


def test_shoot_valid(gpio_mock_on_pi, time_mock, controller):
    controller.shoot(3, 3)

    assert gpio_mock_on_pi.output.call_count == 4
    assert time_mock.sleep.call_count == 2


def test_charge_not_on_pi(gpio_mock_not_on_pi, time_mock, controller):
    controller.charge(0)

    assert gpio_mock_not_on_pi.output.call_count == 0
    assert time_mock.sleep.call_count == 0


def test_charge_invalid_sleep_time(gpio_mock_on_pi, time_mock, controller):
    with pytest.raises(ValueError):
        controller.charge(10)


def test_charge_valid(gpio_mock_on_pi, time_mock, controller):
    controller.charge(2)

    assert gpio_mock_on_pi.output.call(controller.charge_pin,
                                       gpio_mock_on_pi.HIGH)
    assert gpio_mock_on_pi.output.call_count == 2
    assert time_mock.sleep.call_count == 1


def test_load_not_on_pi(gpio_mock_not_on_pi, time_mock, controller):
    controller.load(0)

    assert gpio_mock_not_on_pi.output.call_count == 0
    assert time_mock.sleep.call_count == 0


def test_load_invalid_sleep_time(gpio_mock_on_pi, time_mock, controller):
    with pytest.raises(ValueError):
        controller.load(10)


def test_load_valid(gpio_mock_on_pi, time_mock, controller):
    controller.load(2)

    assert gpio_mock_on_pi.output.call(controller.load_pin,
                                       gpio_mock_on_pi.HIGH)
    assert gpio_mock_on_pi.output.call_count == 2
    assert time_mock.sleep.call_count == 1


def test_default_servo_position(gpio_mock_not_on_pi, controller):
    controller.default_servo_position()

    assert controller.get_x_servo_angle() == 90
    assert controller.get_y_servo_angle() == 90


def test_align(gpio_mock_not_on_pi, controller):
    controller.align(-10, 30)

    assert controller.get_x_servo_angle() == 80
    assert controller.get_y_servo_angle() == 120


def test_assign_pins_not_on_pi(gpio_mock_not_on_pi, controller):
    controller._assign_pins()

    assert gpio_mock_not_on_pi.output.call(controller.x_servo_pin,
                                           gpio_mock_not_on_pi.HIGH)
    assert gpio_mock_not_on_pi.output.call(controller.load_pin,
                                           gpio_mock_not_on_pi.HIGH)


def test_set_x_angle_in_range(gpio_mock_not_on_pi, controller):
    controller._set_x_angle(40)

    assert controller.x_servo_angle == 40


def test_set_x_angle_lower_bound(gpio_mock_not_on_pi, controller):
    controller._set_x_angle(-10)

    assert controller.x_servo_angle == 0


def test_set_x_angle_upper_bound(gpio_mock_not_on_pi, controller):
    controller._set_x_angle(200)

    assert controller.x_servo_angle == 180


def test_set_y_angle_in_range(gpio_mock_not_on_pi, controller):
    controller._set_y_angle(70)

    assert controller.y_servo_angle == 70


def test_set_y_angle_lower_bound(gpio_mock_not_on_pi, controller):
    controller._set_y_angle(-10)

    assert controller.y_servo_angle == 60


def test_set_y_angle_upper_bound(gpio_mock_not_on_pi, controller):
    controller._set_y_angle(200)

    assert controller.y_servo_angle == 120


def test_set_angle(mocker, gpio_mock_on_pi, time_mock):
    servo_mock = mocker.MagicMock()
    controller = PiController(1, 2, 3, 4)
    controller.x_servo = servo_mock
    controller._set_angle(controller.x_servo, 70)

    assert servo_mock.ChangeDutyCycle.call_count == 2
    assert time_mock.sleep.call_count == 1


def test_stop(gpio_mock_on_pi, controller):
    controller.stop()

    assert gpio_mock_on_pi.cleanup.call_count == 1
