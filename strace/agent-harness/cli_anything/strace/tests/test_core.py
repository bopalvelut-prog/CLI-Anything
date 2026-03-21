import unittest
from cli_anything.strace.core.session import Session

class TestSession(unittest.TestCase):
    def test_init(self):
        s = Session()
        self.assertFalse(s.has_project())
        self.assertIsNone(s.project)

    def test_set_project(self):
        s = Session()
        s.set_project({"name": "test", "metadata": {}})
        self.assertTrue(s.has_project())
        self.assertEqual(s.get_project()["name"], "test")

    def test_undo_redo(self):
        s = Session()
        s.set_project({"name": "v1", "metadata": {}})
        s.snapshot("change")
        s.project["name"] = "v2"
        desc = s.undo()
        self.assertEqual(s.get_project()["name"], "v1")
        desc = s.redo()
        self.assertEqual(s.get_project()["name"], "v2")

    def test_status(self):
        s = Session()
        status = s.status()
        self.assertFalse(status["has_project"])
        s.set_project({"name": "test", "metadata": {}})
        status = s.status()
        self.assertTrue(status["has_project"])
        self.assertEqual(status["project_name"], "test")

    def test_list_history(self):
        s = Session()
        s.set_project({"name": "test", "metadata": {}})
        s.snapshot("first")
        s.snapshot("second")
        history = s.list_history()
        self.assertEqual(len(history), 2)

if __name__ == "__main__":
    unittest.main()
