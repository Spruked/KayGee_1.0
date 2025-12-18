%%%% LOCKEAN ETHICS MODULE %%%%
%%% Natural Rights & Social Contract Theory
%%% Immutable A Priori Rules - Cryptographically Signed

:- module(locke, [
    violation/1,
    ethical_score/2,
    natural_right/1,
    social_contract_valid/1,
    consent_based/1
]).

%% =============================================================================
%% NATURAL RIGHTS: Life, Liberty, Property
%% "No one ought to harm another in his life, health, liberty, or possessions"
%% =============================================================================

natural_right(life).
natural_right(liberty).
natural_right(property).
natural_right(health).

% Violations of natural rights
violation(Action) :-
    harms_life(Action),
    \+ self_defence(Action),
    \+ just_punishment(Action),
    !.

violation(Action) :-
    restricts_liberty(Action),
    \+ consented(Action),
    \+ social_contract_override(Action),
    !.

violation(Action) :-
    violates_property(Action),
    \+ compensation_provided(Action),
    !.

%% =============================================================================
%% CONSENT PRINCIPLE: Liberty requires informed consent
%% =============================================================================

consent_based(Action) :-
    requires_consent(Action),
    informed_consent(Action, all_affected_parties).

% Actions that require consent
requires_consent(Action) :- restricts_liberty(Action).
requires_consent(Action) :- uses_property(Action, _).
requires_consent(Action) :- affects_body(Action, _).

% Lack of consent is a violation
violation(Action) :-
    requires_consent(Action),
    \+ informed_consent(Action, _),
    !.

%% =============================================================================
%% SOCIAL CONTRACT: Collective good can override individual rights
%% =============================================================================

% Valid if: benefits collective AND minimally restricts liberty AND consented by majority
social_contract_valid(Action) :-
    benefits_collective(Action, Benefit),
    Benefit > 0.7,  % High collective benefit
    minimal_restriction(Action),
    majority_consent(Action).

% Social contract can override individual liberty restrictions
social_contract_override(Action) :-
    restricts_liberty(Action),
    social_contract_valid(Action),
    proportionate_to_threat(Action).

% Example: quarantine during epidemic
social_contract_override(quarantine) :-
    public_health_emergency(true),
    temporary_measure(quarantine),
    necessary_for_safety(quarantine).

%% =============================================================================
%% EMPIRICISM: Knowledge and confidence from experience
%% =============================================================================

% Weight actions based on empirical evidence
ethical_score(Action, Score) :-
    proven_by_experience(Action, SuccessCount),
    FailureCount is 0,
    SuccessCount > 10,
    Score is 0.9,  % High confidence from repeated success
    \+ violation(Action),
    !.

ethical_score(Action, Score) :-
    proven_by_experience(Action, SuccessCount),
    FailureCount is 0,
    SuccessCount >= 5,
    Score is 0.75,
    \+ violation(Action),
    !.

% Novel actions have lower confidence
ethical_score(Action, 0.5) :-
    \+ proven_by_experience(Action, _),
    \+ violation(Action),
    preserves_natural_rights(Action),
    !.

%% =============================================================================
%% PROPERTY RIGHTS: Labor-based entitlement
%% =============================================================================

% Locke's Labor Theory of Property
rightful_property(Person, Thing) :-
    mixed_labor_with(Person, Thing),
    \+ appropriated_by_other(Thing),
    left_enough_for_others.

violates_property(Action) :-
    takes_property(Action, Thing, FromPerson),
    rightful_property(FromPerson, Thing),
    \+ consented(Action),
    \+ just_compensation(Action, Thing).

%% =============================================================================
%% SELF-PRESERVATION: First natural law
%% =============================================================================

ethical_score(Action, 0.8) :-
    preserves_life(Action, self),
    \+ harms_others(Action),
    \+ violation(Action),
    !.

% Self-defense is justified
ethical_score(self_defence, 0.9) :-
    imminent_threat(true),
    proportional_response(self_defence),
    !.

%% =============================================================================
%% TOLERATION: Respect for different beliefs (within reason)
%% =============================================================================

ethical_score(Action, 0.7) :-
    tolerates_difference(Action),
    \+ harms_others(Action),
    \+ violation(Action),
    !.

% Intolerance of harm-causing beliefs is justified
ethical_score(Action, 0.6) :-
    opposes_harmful_practice(Action),
    protects_natural_rights(Action),
    !.

%% =============================================================================
%% SCORING SYSTEM
%% =============================================================================

% Actions preserving all natural rights
ethical_score(Action, 0.95) :-
    preserves_natural_rights(Action),
    consent_based(Action),
    \+ violation(Action),
    !.

% Actions with consent but minor liberty restriction
ethical_score(Action, 0.75) :-
    restricts_liberty(Action),
    consented(Action),
    proportionate_benefit(Action),
    !.

% Violations of natural rights
ethical_score(Action, 0.0) :-
    violation(Action),
    !.

% Default: neutral if no violation and no special merit
ethical_score(Action, 0.5) :-
    \+ violation(Action),
    !.

%% =============================================================================
%% HELPER PREDICATES
%% =============================================================================

preserves_natural_rights(Action) :-
    \+ harms_life(Action),
    \+ restricts_liberty(Action),
    \+ violates_property(Action).

harms_life(Action) :- action_effect(Action, death).
harms_life(Action) :- action_effect(Action, serious_harm).

restricts_liberty(Action) :- action_effect(Action, coercion).
restricts_liberty(Action) :- action_effect(Action, imprisonment).
restricts_liberty(Action) :- action_effect(Action, movement_restriction).

violates_property(Action) :- action_effect(Action, theft).
violates_property(Action) :- action_effect(Action, destruction_of_property).

benefits_collective(Action, Benefit) :-
    action_outcome(Action, collective_utility, Benefit).

minimal_restriction(Action) :-
    restriction_severity(Action, Severity),
    Severity < 0.3.

proportionate_to_threat(Action) :-
    threat_level(ThreatLevel),
    restriction_severity(Action, RestrictionLevel),
    RestrictionLevel =< ThreatLevel.

%% =============================================================================
%% MODULE METADATA
%% =============================================================================

:- meta_predicate
    module_name(locke),
    module_priority(0.9),  % High priority for natural rights
    module_weight(0.3),    % 30% weight in final score
    immutable(true),
    checksum('LOCKE_V1_CHECKSUM_PLACEHOLDER').

%%% END LOCKEAN MODULE %%%
