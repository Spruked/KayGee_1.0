% Temporal-Causal Reasoning Engine
% Event Calculus for time-based reasoning

% Event Calculus for time-based reasoning
holds_at(F, T) :- 
    initially(F),
    not clipped(F, T).

holds_at(F, T2) :-
    happens(E, T1),
    T1 < T2,
    initiates(E, F),
    not clipped(F, T2).

clipped(F, T2) :-
    happens(E, T1),
    T1 < T2,
    terminates(E, F).

% Causal graph predicates
causes(Action, Effect, Probability) :-
    action(Action),
    effect(Effect),
    causality(Action, Effect, Probability).

% Example: Offering tea at night causes sleep disruption
causes(offer_tea, sleep_disruption, 0.3) :- time(late_night).

% Temporal ethical constraint
violation(Action) :-
    causes(Action, Harm, Prob),
    Prob > 0.5,
    not justified_harm(Harm).

% Define basic actions
action(offer_tea).
action(suggest_meditation).
action(suggest_break).
action(offer_advice).

% Define effects
effect(sleep_disruption).
effect(stress_reduction).
effect(energy_boost).
effect(clarity).

% Causality relationships
causality(suggest_meditation, stress_reduction, 0.7).
causality(suggest_break, energy_boost, 0.6).
causality(offer_advice, clarity, 0.5).

% Time predicates
time(morning) :- current_hour(H), H >= 6, H < 12.
time(afternoon) :- current_hour(H), H >= 12, H < 18.
time(evening) :- current_hour(H), H >= 18, H < 22.
time(late_night) :- current_hour(H), (H >= 22; H < 6).

% Current hour (mock - would be set by system)
current_hour(14).
