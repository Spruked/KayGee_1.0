%%%% HUMEAN ETHICS MODULE %%%%
%%% Moral Sentiment, Utility, and Custom
%%% Immutable A Priori Rules - Cryptographically Signed

:- module(hume, [
    ethical_score/2,
    weight/2,
    violation/1,
    evokes_sympathy/2,
    increases_utility/2
]).

%% =============================================================================
%% MORAL SENTIMENT: Sympathy/empathy as foundation
%% "Morality is more properly felt than judg'd of"
%% =============================================================================

% Primary ethical scoring based on sentiment and sympathy
ethical_score(Action, Score) :-
    evokes_sympathy(Action, SympathyScore),
    SympathyScore > 0,
    Score is SympathyScore * 0.8,
    \+ violation(Action),
    !.

% Evokes sympathy based on emotional resonance
evokes_sympathy(Action, Score) :-
    emotional_resonance(Action, ResonanceLevel),
    promotes_wellbeing(Action, WellbeingLevel),
    Score is (ResonanceLevel * 0.6 + WellbeingLevel * 0.4).

%% =============================================================================
%% IS-OUGHT GAP: Cannot derive "ought" from "is" alone
%% =============================================================================

% Purely descriptive facts have lower weight
weight(Action, 0.5) :-
    solely_descriptive(Action),
    \+ sentiment_component(Action, _),
    !.

% Actions grounded in both fact and sentiment have full weight
weight(Action, 1.0) :-
    factual_basis(Action),
    sentiment_component(Action, _),
    !.

% Violations: No sentiment can justify certain harms
violation(Action) :-
    causes_unnecessary_suffering(Action),
    \+ greater_good_justification(Action),
    !.

%% =============================================================================
%% UTILITY: Greatest happiness principle (proto-utilitarianism)
%% =============================================================================

% Net utility calculation
ethical_score(Action, Score) :-
    increases_utility(Action, UtilityIncrease),
    decreases_utility(Action, UtilityDecrease),
    UtilityIncrease > 0,
    NetUtility is (UtilityIncrease - UtilityDecrease) / (UtilityIncrease + UtilityDecrease + 1),
    Score is NetUtility * 0.9,
    \+ violation(Action),
    !.

% High utility actions
increases_utility(Action, Score) :-
    action_effect(Action, happiness_increase, Magnitude),
    affected_people(Action, Count),
    Score is (Magnitude * Count) / 100.0.  % Normalize

% Utility decrease
decreases_utility(Action, Score) :-
    action_effect(Action, happiness_decrease, Magnitude),
    affected_people(Action, Count),
    Score is (Magnitude * Count) / 100.0.

%% =============================================================================
%% CUSTOM AND HABIT: Past success increases confidence
%% =============================================================================

% Actions that have succeeded in the past get higher weight
weight(Action, Confidence) :-
    succeeded_in_past(Action, SuccessCount),
    SuccessCount > 0,
    Confidence is SuccessCount / (SuccessCount + 1),  % Asymptotic to 1.0
    !.

% Novel actions have baseline weight
weight(Action, 0.5) :-
    \+ succeeded_in_past(Action, _),
    !.

% Actions with mixed history
weight(Action, Confidence) :-
    succeeded_in_past(Action, SuccessCount),
    failed_in_past(Action, FailureCount),
    Total is SuccessCount + FailureCount,
    Confidence is (SuccessCount / Total) * 0.9,  % Discount for uncertainty
    !.

%% =============================================================================
%% ARTIFICIAL vs. NATURAL VIRTUES
%% =============================================================================

% Natural virtues: immediately agreeable (sympathy-based)
natural_virtue(benevolence).
natural_virtue(compassion).
natural_virtue(generosity).
natural_virtue(gratitude).

ethical_score(Action, 0.8) :-
    exemplifies_virtue(Action, Virtue),
    natural_virtue(Virtue),
    \+ violation(Action),
    !.

% Artificial virtues: useful for society (convention-based)
artificial_virtue(justice).
artificial_virtue(promise_keeping).
artificial_virtue(property_respect).

ethical_score(Action, 0.75) :-
    exemplifies_virtue(Action, Virtue),
    artificial_virtue(Virtue),
    socially_beneficial(Action),
    \+ violation(Action),
    !.

%% =============================================================================
%% REASON AS SLAVE OF PASSIONS
%% "Reason is, and ought only to be the slave of the passions"
%% =============================================================================

% Actions aligned with passions AND reason score well
ethical_score(Action, 0.85) :-
    passion_driven(Action, Passion),
    reasonable_means(Action),
    positive_passion(Passion),
    \+ violation(Action),
    !.

positive_passion(love).
positive_passion(joy).
positive_passion(hope).
positive_passion(gratitude).

negative_passion(hatred).
negative_passion(cruelty).
negative_passion(malice).
negative_passion(envy).

% Actions driven by negative passions
ethical_score(Action, 0.2) :-
    passion_driven(Action, Passion),
    negative_passion(Passion),
    !.

%% =============================================================================
%% SYMPATHY: Capacity to feel what others feel
%% =============================================================================

% High sympathy evocation
evokes_sympathy(Action, 0.9) :-
    relieves_suffering(Action, _),
    immediate_and_visible(Action),
    !.

evokes_sympathy(Action, 0.7) :-
    promotes_happiness(Action, _),
    affects_close_others(Action),
    !.

% Low sympathy (distant or abstract)
evokes_sympathy(Action, 0.3) :-
    affects_distant_others(Action),
    abstract_benefit(Action),
    !.

%% =============================================================================
%% JUSTICE AS CONVENTION
%% =============================================================================

% Justice is artificial virtue serving social utility
ethical_score(Action, 0.8) :-
    upholds_justice(Action),
    increases_social_stability(Action),
    \+ violation(Action),
    !.

% Violations of justice harm utility
violation(Action) :-
    violates_justice(Action),
    harms_social_fabric(Action),
    !.

violates_justice(Action) :-
    action_type(Action, theft).
violates_justice(Action) :-
    action_type(Action, breach_of_contract).
violates_justice(Action) :-
    action_type(Action, dishonesty_in_trade).

%% =============================================================================
%% PROPORTION: Matching sentiment to object
%% =============================================================================

% Appropriate emotional response
ethical_score(Action, 0.75) :-
    emotional_response(Action, Emotion),
    appropriate_to_circumstance(Emotion, Action),
    !.

% Disproportionate response
ethical_score(Action, 0.4) :-
    emotional_response(Action, Emotion),
    \+ appropriate_to_circumstance(Emotion, Action),
    !.

%% =============================================================================
%% DEFAULT SCORING
%% =============================================================================

% Neutral actions with no strong sentiment
ethical_score(Action, 0.5) :-
    \+ violation(Action),
    \+ evokes_sympathy(Action, _),
    \+ increases_utility(Action, _),
    !.

% Violations
ethical_score(Action, 0.0) :-
    violation(Action),
    !.

%% =============================================================================
%% HELPER PREDICATES
%% =============================================================================

solely_descriptive(Action) :-
    action_basis(Action, factual_only).

sentiment_component(Action, Sentiment) :-
    emotional_driver(Action, Sentiment).

causes_unnecessary_suffering(Action) :-
    action_effect(Action, suffering, High),
    High > 0.7,
    \+ prevents_greater_harm(Action).

factual_basis(Action) :-
    grounded_in_observation(Action).

reasonable_means(Action) :-
    action_method(Action, rational_plan).

exemplifies_virtue(Action, Virtue) :-
    action_type(Action, Virtue).

socially_beneficial(Action) :-
    action_effect(Action, social_utility, Score),
    Score > 0.5.

passion_driven(Action, Passion) :-
    emotional_driver(Action, Passion).

relieves_suffering(Action, Target) :-
    action_effect(Action, reduce_pain, Target).

promotes_happiness(Action, Target) :-
    action_effect(Action, increase_joy, Target).

immediate_and_visible(Action) :-
    temporal_proximity(Action, immediate),
    observable_outcome(Action, true).

affects_close_others(Action) :-
    social_distance(Action, close).

affects_distant_others(Action) :-
    social_distance(Action, distant).

abstract_benefit(Action) :-
    outcome_type(Action, abstract).

upholds_justice(Action) :-
    action_type(Action, fair_distribution).

increases_social_stability(Action) :-
    action_effect(Action, stability_increase, _).

harms_social_fabric(Action) :-
    action_effect(Action, trust_erosion, High),
    High > 0.6.

appropriate_to_circumstance(Emotion, Action) :-
    circumstance_severity(Action, Severity),
    emotion_intensity(Emotion, Intensity),
    abs(Severity - Intensity) < 0.2.  % Similar magnitude

%% =============================================================================
%% MODULE METADATA
%% =============================================================================

:- meta_predicate
    module_name(hume),
    module_priority(0.6),  % Medium priority (empirical, flexible)
    module_weight(0.25),   % 25% weight in final score
    immutable(true),
    checksum('HUME_V1_CHECKSUM_PLACEHOLDER').

%%% END HUMEAN MODULE %%%
