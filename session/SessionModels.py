from system.console import Color

from error.Exceptions import LauncherFlowInterruptedException


class _BasicDevice:
    def __init__(self, adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller):
        self.adb_controller = adb_controller
        self.adb_package_manager_controller = adb_package_manager_controller
        self.adb_settings_controller = adb_settings_controller
        self.adb_name = adb_name
        self.android_id = None
        self.status = status

    def install_apk(self, apk_file):
        return self.adb_controller.install_apk(self.adb_name, apk_file)

    def list_packages(self):
        return self.adb_package_manager_controller

    def get_installed_packages(self):
        return self.adb_package_manager_controller.get_installed_packages(self.adb_name)

    def uninstall_package(self, package_name):
        return self.adb_package_manager_controller.uninstall_package(self.adb_name, package_name)

    def get_android_id(self):
        if self.android_id is None:
            self.android_id = self.adb_settings_controller.get_device_android_id(self.adb_name).strip()
        return self.android_id


class _BasicVirtualDevice(_BasicDevice):
    def __init__(self, adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller):
        super().__init__(adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller)

    def get_property(self, device_property):
        return self.adb_controller.get_property(self.adb_name, device_property)

    def kill(self):
        return self.adb_controller.kill_device(self.adb_name)


class OutsideSessionDevice(_BasicDevice):
    def __init__(self, adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller):
        super().__init__(adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller)


class OutsideSessionVirtualDevice(_BasicVirtualDevice):
    def __init__(self, adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller):
        super().__init__(adb_name, status, adb_controller, adb_package_manager_controller, adb_settings_controller)


class SessionVirtualDevice(_BasicVirtualDevice):
    TAG = "SessionVirtualDevice:"

    def __init__(self,
                 avd_schema, port, log_file, avdmanager_controller, emulator_controller, adb_controller,
                 adb_package_manager_controller, adb_settings_controller):

        super().__init__("emulator-" + str(port), "not-launched", adb_controller, adb_package_manager_controller,
                         adb_settings_controller)

        self.avdmanager_controller = avdmanager_controller
        self.emulator_controller = emulator_controller
        self.avd_schema = avd_schema
        self._check_avd_schema()

        self.port = port
        self.log_file = log_file

    def _check_avd_schema(self):
        if self.avd_schema.avd_name == "":
            message = "One AVD schema doesn't have name set."
            raise LauncherFlowInterruptedException(self.TAG, message)

        if self.avd_schema.create_avd_package == "":
            message = "Parameter 'create_avd_package' in AVD schema {} cannot be empty."
            message = message.format(self.avd_schema.avd_name)
            raise LauncherFlowInterruptedException(self.TAG, message)

        if self.avd_schema.launch_avd_launch_binary_name == "":
            message = "Parameter 'launch_avd_launch_binary_name' in AVD schema {} cannot be empty."
            message = message.format(self.avd_schema.avd_name)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def create(self):
        return self.avdmanager_controller.create_avd(self.avd_schema)

    def delete(self):
        return self.avdmanager_controller.delete_avd(self.avd_schema)

    def launch(self):
        return self.emulator_controller.launch_avd(self.avd_schema, self.port, self.log_file)

    def apply_config_ini(self):
        return self.emulator_controller.apply_config_to_avd(self.avd_schema)


class ApkCandidate:
    MISSING_VALUE = Color.RED + "missing" + Color.END

    def __init__(self, apk_name, apk_path, test_apk_name, test_apk_path, apk_version):
        self.apk_name = self._set_field(apk_name)
        self.apk_path = self._set_field(apk_path)
        self.test_apk_name = self._set_field(test_apk_name)
        self.test_apk_path = self._set_field(test_apk_path)
        self.apk_version = apk_version

    def is_usable(self):
        return self._is_field_filled(self.apk_name) \
               and self._is_field_filled(self.test_apk_path) \
               and self._is_field_filled(self.test_apk_name) \
               and self._is_field_filled(self.test_apk_path) \
               and self.apk_version != -1

    def __str__(self):
        return "Apk('apk_name: " + self.apk_name + "', " \
               + "'apk_path: " + self.apk_path + "', " \
               + "'test_apk_name: " + self.test_apk_name + "', " \
               + "'test_apk_path: " + self.test_apk_path + "', " \
               + "'version_code: " + str(self.apk_version) + "')"

    def _is_field_filled(self, field):
        return field is not None and field != self.MISSING_VALUE

    def _set_field(self, field):
        return field if field is not None and field != "" else self.MISSING_VALUE


class SessionSummary:
    def __init__(self):
        self.device_summaries = None
        self.time_summary = None
        self.apk_summary = None
        self.test_summary = None


class SessionDeviceSummary:
    def __init__(self):
        self.device_name = None

        self.creation_start_time = None
        self.creation_end_time = None
        self.creation_time = None

        self.launch_start_time = None
        self.launch_end_time = None
        self.launch_time = None

        self.apk_install_start_time = None
        self.apk_install_end_time = None
        self.apk_install_time = None

        self.test_apk_install_start_time = None
        self.test_apk_install_end_time = None
        self.test_apk_install_time = None


class SessionTimeSummary:
    def __init__(self):
        self.total_device_creation_start_time = None
        self.total_device_creation_end_time = None
        self.total_device_creation_time = None

        self.total_device_launch_start_time = None
        self.total_device_launch_end_time = None
        self.total_device_launch_time = None

        self.total_apk_build_start_time = None
        self.total_apk_build_end_time = None
        self.total_apk_build_time = None

        self.total_apk_install_start_time = None
        self.total_apk_install_end_time = None
        self.total_apk_install_time = None

        self.total_test_start_time = None
        self.total_test_end_time = None
        self.total_test_time = None

        self.total_session_start_time = None
        self.total_session_end_time = None
        self.total_session_time = None


class SessionApkSummary:
    def __init__(self):
        self.apk = None
        self.test_apk = None
        self.version_code = None

        self.apk_build_start_time = None
        self.apk_build_end_time = None
        self.apk_build_time = None

        self.test_apk_build_start_time = None
        self.test_apk_build_end_time = None
        self.test_apk_build_time = None


class SessionTestSummary:
    def __init__(self):
        self.test_number = None
        self.test_passed = None
        self.test_failed = None
        self.health_rate = None


class TestSummary:
    def __init__(self):
        self.test_name = None
        self.test_container = None
        self.test_full_package = None
        self.test_status = None
        self.device = None
        self.test_start_time = None

        self.test_end_time = None
        self.error_messages = list()


class TestLogCat:
    def __init__(self):
        self.test_name = None
        self.test_container = None
        self.test_full_package = None
        self.lines = list()


class TestLogCatLine:
    def __init__(self):
        self.date = None
        self.time = None
        self.level = None
        self.tag = None
        self.text = None
