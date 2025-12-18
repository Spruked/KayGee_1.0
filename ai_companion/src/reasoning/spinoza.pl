%%%% SPINOZAN ETHICS MODULE %%%%
%%% Conatus, Determinism, and Intellectual Love
%%% Immutable A Priori Rules - Cryptographically Signed

:- module(spinoza, [
    ethical_score/2,
    weight/2,
    violation/1,
    increases_rationality/2,
    preserves_being/2,
    driven_by_passion/1
]).

%% =============================================================================
%% CONATUS: Striving to preserve one's being
%% "Each thing, as far as it can by its own power, strives to persevere in its being"
%% =============================================================================

% Actions that enhance both reason and self-preservation score highest
ethical_score(Action, Score) :-
    increases_rationality(Action, RationalityScore),
    preserves_being(Action, PreservationScore),
    RationalityScore > 0,
    PreservationScore > 0,
    Score is (RationalityScore * 0.5 + PreservationScore * 0.5),
    \+ violation(Action),
    !.

%% =============================================================================
%% DETERMINISM: All actions necessitated; judge by outcomes
%% =============================================================================

% Violation only if harm is near-certain (>0.9 probability)
violation(Action) :-
    leads_to_harm(Action, Certainty),
    Certainty > 0.9,
    !.

% Lesser certainty of harm reduces ethical score but isn't a violation
ethical_score(Action, Score) :-
    leads_to_harm(Action, Certainty),
    Certainty =< 0.9,
    Certainty > 0.5,
    Score is (1.0 - Certainty) * 0.5,  % Scaled penalty
    !.

%% =============================================================================
%% ADEQUATE IDEAS: Understanding vs. Imagination
%% =============================================================================

% Actions based on reason (adequate ideas) score higher
weight(Action, 0.9) :-
    based_on_adequate_knowledge(Action),
    \+ driven_by_passion(Action),
    !.

% Actions driven by passion (inadequate ideas) are discounted
weight(Action, 0.3) :-
    driven_by_passion(Action),
    !.

% Mixed actions (some reason, some passion)
weight(Action, 0.6) :-
    partially_reasoned(Action),
    !.

%% =============================================================================
%% PASSIONS vs. ACTIVE EMOTIONS
%% =============================================================================

% Passive emotions (passions): sadness, anger, fear - decrease power
driven_by_passion(Action) :-
    emotion_driver(Action, Emotion),
    passive_emotion(Emotion).

passive_emotion(sadness).
passive_emotion(anger).
passive_emotion(fear).
passive_emotion(envy).
passive_emotion(hatred).

% Active emotions: joy from understanding - increase power
ethical_score(Action, 0.85) :-
    emotion_driver(Action, Emotion),
    active_emotion(Emotion),
    \+ violation(Action),
    !.

active_emotion(joy_from_understanding).
active_emotion(intellectual_love).
active_emotion(amor_dei_intellectualis).  % Love of God/Nature

%% =============================================================================
%% INTELLECTUAL LOVE: Highest good is understanding
%% =============================================================================

% Actions increasing understanding receive highest scores
ethical_score(Action, 0.95) :-
    increases_understanding(Action),
    promotes_adequate_knowledge(Action),
    \+ violation(Action),
    !.

% Education, contemplation, scientific inquiry
increases_understanding(Action) :-
    action_type(Action, education).
increases_understanding(Action) :-
    action_type(Action, contemplation).
increases_understanding(Action) :-
    action_type(Action, scientific_inquiry).

%% =============================================================================
%% BLESSEDNESS: Freedom from passive emotions
%% =============================================================================

ethical_score(Action, 0.8) :-
    reduces_passive_emotions(Action),
    increases_active_power(Action),
    !.

% Actions that liberate from bondage to passions
reduces_passive_emotions(Action) :-
    action_effect(Action, emotional_regulation).
reduces_passive_emotions(Action) :-
    action_effect(Action, mindfulness).

%% =============================================================================
%% SELF-PRESERVATION vs. COLLECTIVE GOOD
%% =============================================================================

% Preserving one's rational being
preserves_being(Action, Score) :-
    action_effect(Action, self_preservation, DirectScore),
    action_effect(Action, harm_to_others, HarmScore),
    Score is DirectScore - (HarmScore * 0.5),  % Penalty for harming others
    Score >= 0,
    !.

preserves_being(Action, 0.5) :-
    \+ harms_self(Action),
    \+ harms_others(Action),
    !.

%% =============================================================================
%% RATIONALITY: Clear and distinct perception
%% =============================================================================

increases_rationality(Action, Score) :-
    clarity_of_perception(Action, Clarity),
    distinctness_of_ideas(Action, Distinctness),
    Score is (Clarity + Distinctness) / 2.0,
    !.

% Actions promoting rational capacity
increases_rationality(Action, 0.8) :-
    action_effect(Action, enhances_reason),
    !.

% Actions impairing rationality
increases_rationality(Action, 0.1) :-
    action_effect(Action, impairs_reason),
    !.

%% =============================================================================
%% MONISM: Actions harmonizing with Nature score higher
%% =============================================================================

ethical_score(Action, 0.75) :-
    aligns_with_natural_order(Action),
    \+ violates_natural_laws(Action),
    \+ violation(Action),
    !.

aligns_with_natural_order(Action) :-
    sustainable(Action),
    promotes_harmony(Action).

%% =============================================================================
%% FREE WILL vs. NECESSITY
%% =============================================================================

% Spinoza denies free will, but acknowledges degrees of freedom (rationality)
degree_of_freedom(Action, Degree) :-
    rationality_level(Action, RationalityLevel),
    Degree is RationalityLevel.  % More rational = more free

% Actions with higher freedom score better
ethical_score(Action, Score) :-
    degree_of_freedom(Action, Freedom),
    Freedom > 0.7,
    Score is Freedom * 0.8,
    \+ violation(Action),
    !.

%% =============================================================================
%% DEFAULT SCORING
%% =============================================================================

% Neutral actions
ethical_score(Action, 0.5) :-
    \+ violation(Action),
    \+ increases_understanding(Action),
    \+ driven_by_passion(Action),
    !.

% Violations
ethical_score(Action, 0.0) :-
    violation(Action),
    !.

% Default weight for unclassified actions
weight(Action, 0.5) :-
    \+ driven_by_passion(Action),
    \+ based_on_adequate_knowledge(Action),
    !.

%% =============================================================================
%% HELPER PREDICATES
%% =============================================================================

based_on_adequate_knowledge(Action) :-
    knowledge_basis(Action, adequate_ideas).

based_on_adequate_knowledge(Action) :-
    rational_deliberation(Action, true).

partially_reasoned(Action) :-
    rational_component(Action, Score),
    Score > 0.3,
    Score < 0.7.

promotes_adequate_knowledge(Action) :-
    action_effect(Action, increases_knowledge).

leads_to_harm(Action, Certainty) :-
    action_outcome(Action, harm, Probability),
    Certainty is Probability.

harms_self(Action) :- action_effect(Action, self_harm).
harms_others(Action) :- action_effect(Action, harm_others).

increases_active_power(Action) :-
    action_effect(Action, empowerment).

sustainable(Action) :-
    \+ depletes_resources(Action).

promotes_harmony(Action) :-
    action_effect(Action, social_harmony).

violates_natural_laws(Action) :-
    action_type(Action, supernatural_belief).  % Spinoza rejects miracles

%% =============================================================================
%% MODULE METADATA
%% =============================================================================

:- meta_predicate
    module_name(spinoza),
    module_priority(0.7),  % Medium-high priority
    module_weight(0.2),    % 20% weight in final score
    immutable(true),
    checksum('SPINOZA_V1_CHECKSUM_PLACEHOLDER').

%%% END SPINOZAN MODULE %%%
