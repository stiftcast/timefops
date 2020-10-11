#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import os
import random
import uuid
import collections
from timefops import Timefops 


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.tf = Timefops()

    @mock.patch('os.path.ismount')
    def test_one(self, mock_method):
        """Makes sure the function correctly detects the mount point."""
        mock_method.return_value = True
        self.assertEqual(os.getcwd(), self.tf.find_mount_point(os.getcwd()))

    def test_renaming(self):
        """Ensures enumeration suffix is added in the correct place, depending
        on if the object is a file or a directory.
        """
        self.assertEqual(self.tf.add_enumerate("dir", 1), "dir(1)")
        self.assertEqual(self.tf.add_enumerate("file.txt", 3), "file(3).txt")

    def test_duplicate_handling(self):
        """Ensure that duplicates are handled correctly, so that no dir/file
        gets overwritten. This also ensures that names are differentiated from
        each other, even when they fall on the same date.
        """

        mock_files = ("unit", "test")
        test_data = {}
        for _ in range(0, 100):
            test_data[os.path.join(
                str(uuid.uuid4()), random.choice(mock_files))
                     ] = random.choice(("2017", "2018", "2019", "2020"))

        file_count = list(map(collections.Counter, [
            [v for k, v in test_data.items() if os.path.basename(k) == f]
            for f in mock_files
        ]))

        count_pair = zip(file_count, mock_files)
        fn_dict, dup_dict = self.tf._rename_duplicates(test_data)

        for count, item in count_pair:
            for v, occur in count.items():
                if occur > 1:
                    # Sort test
                    self.assertEqual(occur, len(dup_dict[v].get(item)))

                    # Enumeration test (renaming)
                    self.assertEqual(fn_dict.get(dup_dict[v].get(item)[-1]),
                                     "{}({})".format(
                                         item, len(dup_dict[v].get(item)) - 1))


if __name__ == '__main__':
    unittest.main()
