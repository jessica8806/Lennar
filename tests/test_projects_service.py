import unittest

from civicsignal.projects_service import get_project, list_projects


class ProjectsServiceTests(unittest.TestCase):
    def test_list_projects_returns_grouped_timeline(self) -> None:
        response = list_projects(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
        )

        self.assertGreaterEqual(response.total, 1)
        project = response.items[0]
        self.assertTrue(project.project_id)
        self.assertTrue(project.project_name)
        self.assertGreaterEqual(project.signals_count, 1)
        self.assertGreaterEqual(len(project.timeline), 1)
        self.assertLessEqual(project.first_detected, project.latest_activity)

    def test_get_project_returns_detail(self) -> None:
        projects = list_projects(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            limit=1,
        )
        project_id = projects.items[0].project_id

        detail = get_project(
            project_id=project_id,
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
        )
        self.assertEqual(detail.project_id, project_id)
        self.assertGreaterEqual(len(detail.timeline), 1)

    def test_get_project_raises_for_missing_project(self) -> None:
        with self.assertRaises(KeyError):
            get_project(
                project_id="missing-project-id",
                start_date="2026-03-01",
                end_date="2026-03-03",
                city="fullerton",
            )

    def test_list_projects_supports_keyword_filter(self) -> None:
        response = list_projects(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            keyword="planning",
        )
        self.assertGreaterEqual(response.total, 1)


if __name__ == "__main__":
    unittest.main()
