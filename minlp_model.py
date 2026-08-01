from pyomo.environ import *


def default_config():
    return {

        "feeds": [
            "F1",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
        ],

        "tanks": [
            "T1",
            "T2",
            "T3",
        ],

        "feed_max_flow": {
            "F1": 60,
            "F2": 70,
            "F3": 50,
            "F4": 80,
            "F5": 60,
            "F6": 40,
        },

        "feed_sulfur": {
            "F1": 0.20,
            "F2": 0.35,
            "F3": 0.60,
            "F4": 1.10,
            "F5": 1.50,
            "F6": 2.20,
        },

        "feed_margin": {
            "F1": 14,
            "F2": 12,
            "F3": 18,
            "F4": 25,
            "F5": 30,
            "F6": 35,
        },

        "feed_startup_cost": {
            "F1": 100,
            "F2": 100,
            "F3": 120,
            "F4": 150,
            "F5": 180,
            "F6": 200,
        },

        "min_feed_nomination": 10,

        "cdu_min_throughput": 220,
        "cdu_max_throughput": 250,

        "cdu_sulfur_spec": 0.85,
    }


def build_model(config=None):

    if config is None:
        config = default_config()

    m = ConcreteModel("Crude_Scheduling_MINLP")

    # ======================================================
    # STORE CONFIG ON MODEL
    # ======================================================

    m.config = config

    # ======================================================
    # SETS
    # ======================================================

    m.FEEDS = Set(
        initialize=config["feeds"]
    )

    m.TANKS = Set(
        initialize=config["tanks"]
    )

    # ======================================================
    # VARIABLES
    # ======================================================

    m.feed_to_tank_flow = Var(
        m.FEEDS,
        m.TANKS,
        domain=NonNegativeReals
    )

    m.tank_to_cdu_flow = Var(
        m.TANKS,
        domain=NonNegativeReals
    )

    m.tank_sulfur = Var(
        m.TANKS,
        bounds=(0, 3)
    )

    m.cdu_sulfur = Var(
        bounds=(0, 3)
    )

    m.feed_active = Var(
        m.FEEDS,
        domain=Binary
    )

    # ======================================================
    # EXPRESSIONS
    # ======================================================

    def cdu_flow_rule(m):
        return sum(
            m.tank_to_cdu_flow[t]
            for t in m.TANKS
        )

    m.cdu_flow = Expression(
        rule=cdu_flow_rule
    )

    # ======================================================
    # FEED CAPACITY
    # ======================================================

    def feed_capacity_rule(m, feed):

        return (

            sum(
                m.feed_to_tank_flow[feed, tank]
                for tank in m.TANKS
            )

            <=

            config["feed_max_flow"][feed]
            *
            m.feed_active[feed]

        )

    m.feed_capacity = Constraint(
        m.FEEDS,
        rule=feed_capacity_rule
    )

    # ======================================================
    # MINIMUM FEED NOMINATION
    # ======================================================

    def feed_minimum_nomination_rule(
        m,
        feed
    ):

        return (

            sum(
                m.feed_to_tank_flow[feed, tank]
                for tank in m.TANKS
            )

            >=

            config["min_feed_nomination"]
            *
            m.feed_active[feed]

        )

    m.feed_minimum_nomination = Constraint(
        m.FEEDS,
        rule=feed_minimum_nomination_rule
    )

    # ======================================================
    # TANK MATERIAL BALANCE
    # ======================================================

    def tank_material_balance_rule(
        m,
        tank
    ):

        return (

            sum(
                m.feed_to_tank_flow[feed, tank]
                for feed in m.FEEDS
            )

            ==

            m.tank_to_cdu_flow[tank]

        )

    m.tank_material_balance = Constraint(
        m.TANKS,
        rule=tank_material_balance_rule
    )

    # ======================================================
    # TANK SULFUR BALANCE
    # ======================================================

    def tank_sulfur_balance_rule(
        m,
        tank
    ):

        incoming_sulfur = sum(

            config["feed_sulfur"][feed]
            *
            m.feed_to_tank_flow[feed, tank]

            for feed in m.FEEDS

        )

        outgoing_sulfur = (

            m.tank_sulfur[tank]
            *
            m.tank_to_cdu_flow[tank]

        )

        return incoming_sulfur == outgoing_sulfur

    m.tank_sulfur_balance = Constraint(
        m.TANKS,
        rule=tank_sulfur_balance_rule
    )

    # ======================================================
    # CDU SULFUR BALANCE
    # ======================================================

    def cdu_sulfur_balance_rule(m):

        incoming_sulfur = sum(

            m.tank_sulfur[tank]
            *
            m.tank_to_cdu_flow[tank]

            for tank in m.TANKS

        )

        outgoing_sulfur = (

            m.cdu_sulfur
            *
            m.cdu_flow

        )

        return incoming_sulfur == outgoing_sulfur

    m.cdu_sulfur_balance = Constraint(
        rule=cdu_sulfur_balance_rule
    )

    # ======================================================
    # CDU THROUGHPUT
    # ======================================================

    m.cdu_minimum_throughput = Constraint(
        expr=
        m.cdu_flow
        >=
        config["cdu_min_throughput"]
    )

    m.cdu_maximum_throughput = Constraint(
        expr=
        m.cdu_flow
        <=
        config["cdu_max_throughput"]
    )

    # ======================================================
    # CDU SULFUR SPEC
    # ======================================================

    m.cdu_sulfur_specification = Constraint(
        expr=
        m.cdu_sulfur
        <=
        config["cdu_sulfur_spec"]
    )

    # ======================================================
    # OBJECTIVE
    # ======================================================

    def profit_rule(m):

        feed_profit = sum(

            config["feed_margin"][feed]
            *
            m.feed_to_tank_flow[feed, tank]

            for feed in m.FEEDS
            for tank in m.TANKS

        )

        feed_activation_penalty = sum(

            config["feed_startup_cost"][feed]
            *
            m.feed_active[feed]

            for feed in m.FEEDS

        )

        return (

            feed_profit

            -

            feed_activation_penalty

        )

    m.total_profit = Objective(
        rule=profit_rule,
        sense=maximize
    )

    return m