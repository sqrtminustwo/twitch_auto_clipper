from socket import timeout
from twitch_auto_clipper.utils.ProtectedVar import ProtectedVar, ProtectedVarWaitTimeOut

import unittest
from threading import Thread
from tests.helpers import (
    create_threads,
    id,
    join_all,
    sleep_conditionally,
    start_all,
    for_testing_protected,
)
from tests.utils.LockedCounter import LockedCounter


class TestProtectedVar(unittest.TestCase):
    def catched_wait(self, var, cond=id):
        try:
            if cond is None:
                var.wait()
            else:
                var.wait(cond)
        except ProtectedVarWaitTimeOut:
            pass

    def test_is_waiting(self):
        var = ProtectedVar(False)

        t = Thread(target=lambda: self.catched_wait(var))
        t.start()

        sleep_conditionally(not var.is_waiting())

        self.assertTrue(var.is_waiting())

        var.value = True

        t.join()
        self.assertFalse(var.is_waiting())

    def test_set(self):
        var = ProtectedVar(False)

        done_waiting_count = LockedCounter()

        def waiter():
            nonlocal done_waiting_count
            self.catched_wait(var)
            done_waiting_count += 1

        wait_threads = create_threads(waiter)
        start_all(wait_threads)

        var.value = True

        num_of_threads = len(wait_threads)
        sleep_conditionally(done_waiting_count < num_of_threads)

        join_all(wait_threads)
        self.assertEqual(done_waiting_count, num_of_threads)

    def wait_common(self, initial, to_set, cond=None):
        var = ProtectedVar(initial)

        def waiter():
            self.catched_wait(var, cond)
            self.assertEqual(var.value, to_set)

        t = Thread(target=waiter)
        t.start()

        var.value = to_set

        t.join()

    def test_wait_default_cond(self):
        self.wait_common(None, 123)

    def test_wait(self):
        self.wait_common("abc", "abcd", lambda str: len(str) > 3)

    def test_protecting(self):
        var = ProtectedVar(False)

        done = ProtectedVar(False)

        protected_counter = LockedCounter()

        def waiter():
            nonlocal protected_counter

            with var.protecting(True, False) as protecting:
                if protecting:
                    protected_counter += 1
                    return

                done.wait(id)

        wait_threads = for_testing_protected(waiter, done)

        should_be_protected = len(wait_threads) - 1
        sleep_conditionally(protected_counter < should_be_protected)

        done.value = True
        join_all(wait_threads)
        self.assertEqual(protected_counter, should_be_protected)


if __name__ == "__main__":
    unittest.main()
