# Copyright (C) 2018 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess


class GitConfigParser:
    def __init__(self, config_path):
        self.path = config_path

    def _execute_shell_command_and_get_output_lines(self, command):
        sub_process_run = subprocess.run(
            command.split(), stdout=subprocess.PIPE, check=True, universal_newlines=True
        )
        return [line.strip() for line in sub_process_run.stdout.splitlines()]

    def _get_value(self, key):
        command = f"git config -f {self.path} --get {key}"
        return self._execute_shell_command_and_get_output_lines(command)

    def list(self):
        command = f"git config -f {self.path} --list"
        options = self._execute_shell_command_and_get_output_lines(command)
        option_list = []
        for opt in options:
            full_key, value = opt.split("=", 1)
            parsed_opt = {"value": value}
            full_key = full_key.split(".")
            parsed_opt["section"] = full_key[0]
            if len(full_key) == 2:
                parsed_opt["subsection"] = None
                parsed_opt["key"] = full_key[1]
            elif len(full_key) == 3:
                parsed_opt["subsection"] = full_key[1]
                parsed_opt["key"] = full_key[2]
            option_list.append(parsed_opt)

        return option_list

    def get(self, key, default=None):
        """
        Returns value of given key in the configuration file. If the key appears
        multiple times, the last value is returned.
        """
        try:
            return self._get_value(key)[-1]
        except subprocess.CalledProcessError:
            return default

    def get_boolean(self, key, default=False):
        """
        Returns boolean value of given key in the configuration file. If the key
        appears multiple times, the last value is returned.
        """
        if not isinstance(default, bool):
            raise TypeError("Default has to be a boolean.")

        try:
            value = self._get_value(key)[-1].lower()
            if value not in ["true", "false"]:
                raise TypeError("Value is not a boolean.")
            return value == "true"
        except subprocess.CalledProcessError:
            return default
