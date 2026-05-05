from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from student.management.commands.create_student_accounts import Command


class CreateStudentAccountsCommandTests(TestCase):
    def test_create_student_account_uses_student_id_as_username_and_password(self):
        command = Command()
        command.stdout = MagicMock()
        command.style = SimpleNamespace(
            WARNING=lambda message: message,
            SUCCESS=lambda message: message,
            ERROR=lambda message: message,
        )

        student = SimpleNamespace(
            student_id="26100001",
            student_code="HS260001",
            first_name="An",
            last_name="Nguyen",
            user=None,
            save=MagicMock(),
            get_full_name=lambda: "Nguyen An",
        )

        with patch(
            "student.management.commands.create_student_accounts.User.objects.create_user"
        ) as create_user:
            create_user.return_value = SimpleNamespace()
            command.create_student_account(student)

        create_user.assert_called_once()
        kwargs = create_user.call_args.kwargs
        self.assertEqual(kwargs["username"], "26100001")
        self.assertEqual(kwargs["password"], "26100001")

    def test_create_student_account_skips_when_student_id_missing(self):
        command = Command()
        command.stdout = MagicMock()
        command.style = SimpleNamespace(
            WARNING=lambda message: message,
            SUCCESS=lambda message: message,
            ERROR=lambda message: message,
        )

        student = SimpleNamespace(
            student_id="",
            student_code="HS260001",
            first_name="An",
            last_name="Nguyen",
            user=None,
            save=MagicMock(),
            get_full_name=lambda: "Nguyen An",
        )

        with patch(
            "student.management.commands.create_student_accounts.User.objects.create_user"
        ) as create_user:
            command.create_student_account(student)

        create_user.assert_not_called()
