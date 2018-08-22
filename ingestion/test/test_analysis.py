from unittest import TestCase
import ingestion.analysis as analysis


class TestAnalysis(TestCase):
    def test_dict_access(self):
        obj = {
            "subobj1": {
                "subobj2":  {
                    "subobj3": {
                        "a": 1
                    }
                }
            }
        }

        # Valid access
        t2 = analysis.dict_access(obj, "subobj1")
        self.assertEqual(t2, obj["subobj1"])

        t2 = analysis.dict_access(obj, "subobj1.subobj2")
        self.assertEqual(t2, obj["subobj1"]["subobj2"])

        t3 = analysis.dict_access(obj, "subobj1.subobj2.subobj3")
        self.assertEqual(t3, obj["subobj1"]["subobj2"]["subobj3"])

        # Invalid access should return None without throwing
        self.assertEqual(analysis.dict_access(obj, "invalid"), None)
        self.assertEqual(analysis.dict_access(obj, "subobj1.invalid"), None)
        self.assertEqual(analysis.dict_access(obj, "subobj1..invalid"), None)
        self.assertEqual(analysis.dict_access(obj, "subobj1.subobj2."), None)

    def test_growth(self):
        records = [
            {"date": 10, "price": 2.7, "subscribers": 110},
            {"date": 9, "price": 2.11, "subscribers": 115},
            {"date": 8, "price": 2.51, "subscribers": 120},
            {"date": 7, "price": 4.52, "subscribers": 75},
            {"date": 6, "price": 3.732, "subscribers": 50},
            {"date": 5, "price": 3.3223, "subscribers": 37},
            {"date": 4, "price": 2.12, "subscribers": 34},
            {"date": 3, "price": 2.5, "subscribers": 33},
            {"date": 2, "price": 3, "subscribers": 30},
            {"date": 1, "price": 1, "subscribers": 10}
        ]

        self.assertEqual(analysis.growth(records, "price", 1, 10), (1.7000000000000002, 1.7000000000000002))
        self.assertEqual(analysis.growth(records, "subscribers", 1, 10), (100, 10.0))

        self.assertEqual(analysis.growth(records, "price", 1, 5), (2.3223, 2.3223))
        self.assertEqual(analysis.growth(records, "subscribers", 1, 5), (27, 2.7))

        self.assertEqual(analysis.growth(records, "price", 1, 23), (1.7000000000000002, 1.7000000000000002))
        self.assertEqual(analysis.growth(records, "subscribers", 1, 23), (100, 10.0))

        # invalid record key
        self.assertEqual(analysis.growth(records, "volume", 1, 5), (0, 0))

        # invalid date range (start before end)
        with self.assertRaises(ValueError):
            analysis.growth(records, "price", 5, 1)
