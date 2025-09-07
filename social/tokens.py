from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int
from datetime import datetime

class ShortLivedActivationTokenGenerator(PasswordResetTokenGenerator):
    timeout_minutes = 15

    def _make_hash_value(self, user, timestamp):
        login_ts = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return f"{user.pk}{user.password}{login_ts}{user.is_active}{timestamp}"

    def check_token(self, user, token):
        print("✅ check_token called for user:", user)

        is_valid_signature = super().check_token(user, token)
        print("🔐 is_valid_signature:", is_valid_signature)
        if not is_valid_signature:
            return False


        try:
            ts_b36, _ = token.split("-")
            ts = base36_to_int(ts_b36)
        except Exception as e:
            print("❌ token split failed:", e)
            return False

        now_ts = int((datetime.now() - datetime(2001, 1, 1)).total_seconds() // 60)
        diff = now_ts - ts

        print("📦 Token timestamp:", ts)
        print("⏰ Now timestamp:", now_ts)
        print("📉 Diff:", diff, "minutes")
        print("🛑 Timeout limit:", self.timeout_minutes)

        if diff > self.timeout_minutes:
            print("❌ Token expired.")
            return False

        return True
