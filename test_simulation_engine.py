from unittest.mock import MagicMock
import simulation_engine


# UNIT


def test_calculate_density_low():
    assert simulation_engine.calculate_density(10) == "LOW"


def test_calculate_density_medium():
    assert simulation_engine.calculate_density(50) == "MEDIUM"


def test_calculate_density_high():
    assert simulation_engine.calculate_density(80) == "HIGH"


def test_density_boundary_low_to_medium():
    assert simulation_engine.calculate_density(44) == "LOW"
    assert simulation_engine.calculate_density(45) == "MEDIUM"


def test_density_boundary_medium_to_high():
    assert simulation_engine.calculate_density(54) == "MEDIUM"
    assert simulation_engine.calculate_density(55) == "HIGH"


def test_create_people_count():
    people = simulation_engine.create_people(100)
    assert len(people) == 100


def test_create_people_structure():
    people = simulation_engine.create_people(10)

    for p in people:
        assert "id" in p
        assert "zone" in p
        assert "x" in p
        assert "y" in p


def test_create_people_zone_valid():
    people = simulation_engine.create_people(20)

    for p in people:
        assert p["zone"] in simulation_engine.zones


def test_calculate_zone_counts():
    people = [
        {"zone": "MainStage"},
        {"zone": "MainStage"},
        {"zone": "FoodCourt"}
    ]

    counts = simulation_engine.calculate_zone_counts(people)

    assert counts["MainStage"] == 2
    assert counts["FoodCourt"] == 1


def test_move_bounds():
    person = {"x": 50, "y": 50}

    updated = simulation_engine.move_person(person)

    assert 0 <= updated["x"] <= 100
    assert 0 <= updated["y"] <= 100


def test_move_changes_position():
    person = {"x": 50, "y": 50}

    updated = simulation_engine.move_person(person)

    assert updated["x"] != 50 or updated["y"] != 50


# INTEGRATION


def test_update_person_db():
    cursor = MagicMock()

    simulation_engine.update_person_in_db(cursor, {
        "id": 1,
        "zone": "MainStage",
        "x": 10,
        "y": 20
    })

    cursor.execute.assert_called_once()


def test_update_zone_status_db():
    cursor = MagicMock()

    simulation_engine.update_zone_status_in_db(
        cursor,
        "MainStage",
        60
    )

    cursor.execute.assert_called_once()


def test_simulation_step_runs():
    cursor = MagicMock()

    people = simulation_engine.create_people(10)

    result = simulation_engine.simulation_step(people, cursor)

    assert isinstance(result, dict)
    assert cursor.execute.called


def test_simulation_step_updates_all_zones():
    cursor = MagicMock()

    people = simulation_engine.create_people(50)

    result = simulation_engine.simulation_step(people, cursor)

    # ensure all zones exist in output
    for zone in simulation_engine.zones.keys():
        assert zone in result


# EDGE CASE TESTS


def test_empty_people():
    cursor = MagicMock()

    result = simulation_engine.simulation_step([], cursor)

    assert result == {zone: 0 for zone in simulation_engine.zones.keys()}


def test_single_person():
    cursor = MagicMock()

    people = [{
        "id": 1,
        "zone": "MainStage",
        "x": 10,
        "y": 10
    }]

    result = simulation_engine.simulation_step(people, cursor)

    assert result["MainStage"] == 1


def test_invalid_zone_handling():
    people = [{"zone": "UNKNOWN_ZONE"}]

    counts = simulation_engine.calculate_zone_counts(people)

    assert isinstance(counts, dict)


def test_zero_people_density_output():
    counts = simulation_engine.calculate_zone_counts([])

    for zone in simulation_engine.zones:
        assert counts[zone] == 0


def test_invalid_zone_handling():
    people = [{"zone": "UNKNOWN_ZONE"}]

    counts = simulation_engine.calculate_zone_counts(people)

    assert isinstance(counts, dict)

    assert sum(counts.values()) == 0


def test_missing_zone_key():
    people = [{"id": 1, "x": 10, "y": 10}]  # no zone key

    try:
        counts = simulation_engine.calculate_zone_counts(people)
        assert isinstance(counts, dict)
    except KeyError:
        assert False, "Function should handle missing zone safely"


def test_calculate_zone_counts_empty_list():
    counts = simulation_engine.calculate_zone_counts([])

    assert isinstance(counts, dict)
    assert all(v == 0 for v in counts.values())


def test_move_person_negative_values():
    person = {"x": -50, "y": -20}

    updated = simulation_engine.move_person(person)

    assert 0 <= updated["x"] <= 100
    assert 0 <= updated["y"] <= 100


def test_move_person_extreme_values():
    person = {"x": 9999, "y": -9999}

    updated = simulation_engine.move_person(person)

    assert 0 <= updated["x"] <= 100
    assert 0 <= updated["y"] <= 100


def test_simulation_step_no_people():
    cursor = MagicMock()

    result = simulation_engine.simulation_step([], cursor)

    assert isinstance(result, dict)
    assert all(v == 0 for v in result.values())


def test_simulation_large_population():
    cursor = MagicMock()

    people = simulation_engine.create_people(5000)

    result = simulation_engine.simulation_step(people, cursor)

    assert isinstance(result, dict)
    assert sum(result.values()) == 5000


def test_density_edge_boundaries():
    assert simulation_engine.calculate_density(44) == "LOW"
    assert simulation_engine.calculate_density(45) == "MEDIUM"
    assert simulation_engine.calculate_density(54) == "MEDIUM"
    assert simulation_engine.calculate_density(55) == "HIGH"


def test_update_person_missing_fields():
    cursor = MagicMock()

    person = {"id": 1}

    simulation_engine.update_person_in_db(cursor, person)

    assert True

    assert not cursor.execute.called


def test_simulation_step_stability():
    cursor = MagicMock()

    people = simulation_engine.create_people(20)

    for _ in range(5):  # multiple steps
        result = simulation_engine.simulation_step(people, cursor)

        assert isinstance(result, dict)
        assert sum(result.values()) == 20
