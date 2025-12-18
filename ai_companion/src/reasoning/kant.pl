%%%% KANTIAN ETHICS MODULE %%%%
%%% Categorical Imperative & Duty-Based Morality
%%% Immutable A Priori Rules - Cryptographically Signed

:- module(kant, [
    violation/1,
    ethical_score/2,
    universalizable/1,
    uses_mere_means/2,
    perfect_duty/1,
    imperfect_duty/1
]).

%% =============================================================================
%% CATEGORICAL IMPERATIVE: Universalizability Test
%% "Act only according to that maxim whereby you can, at the same time, will 
%%  that it should become a universal law"
%% =============================================================================

% Absolute violations - Perfect Duties (non-derogable)
violation(Action) :-
    \+ universalizable(Action),
    !.  % Cut: if not universalizable, it's a violation

violation(Action) :-
    deceives(Action),
    !.  % Lying is always wrong (no exceptions)

violation(Action) :-
    uses_mere_means(Action, Person),
    Person \= initiator(Action),
    !.  % Cannot treat others as mere means

violation(Action) :-
    breaks_promise(Action),
    \+ overridden_by_higher_duty(Action),
    !.  % Promise-breaking violates perfect duty

violation(Action) :-
    harms_rational_nature(Action),
    !.  % Cannot destroy capacity for reason

%% =============================================================================
%% PERFECT DUTIES: Absolute, non-negotiable
%% =============================================================================

perfect_duty(honesty).
perfect_duty(promise_keeping).
perfect_duty(respect_for_persons).
perfect_duty(non_violence).

% Check if action violates a perfect duty
violates_perfect_duty(Action) :-
    perfect_duty(Duty),
    violates(Action, Duty).

%% =============================================================================
%% IMPERFECT DUTIES: Obligatory but flexible in application
%% =============================================================================

imperfect_duty(helping_others).
imperfect_duty(self_development).
imperfect_duty(gratitude).
imperfect_duty(cultivating_talents).

% Imperfect duties give positive ethical score but are not violations if omitted
ethical_score(Action, 0.7) :-
    helps_others(Action),
    \+ violation(Action),
    !.

ethical_score(Action, 0.75) :-
    develops_rational_capacity(Action),
    \+ violation(Action),
    !.

ethical_score(Action, 0.65) :-
    shows_gratitude(Action),
    \+ violation(Action),
    !.

%% =============================================================================
%% HUMANITY FORMULATION: Never treat as mere means
%% =============================================================================

% Action uses someone as mere means if:
uses_mere_means(Action, Person) :-
    involves_person(Action, Person),
    \+ informed_consent(Action, Person),
    benefits_initiator(Action),
    \+ benefits_person(Action, Person).

uses_mere_means(Action, Person) :-
    manipulates(Action, Person),
    !.

uses_mere_means(Action, Person) :-
    coerces(Action, Person),
    !.

%% =============================================================================
%% UNIVERSALIZABILITY TEST
%% =============================================================================

% An action is universalizable if it can be willed as a universal law
% without logical contradiction or practical impossibility

universalizable(Action) :-
    \+ leads_to_contradiction(Action),
    \+ leads_to_practical_impossibility(Action),
    preserves_moral_law(Action).

% Lying fails universalizability: if everyone lied, communication impossible
leads_to_contradiction(lie).
leads_to_contradiction(break_promise).
leads_to_contradiction(theft).

% Actions that make their own conditions impossible
leads_to_practical_impossibility(Action) :-
    requires_trust(Action),
    universal_adoption_destroys_trust(Action).

%% =============================================================================
%% KINGDOM OF ENDS: Actions must respect rational nature
%% =============================================================================

harms_rational_nature(Action) :-
    impairs_autonomy(Action).

harms_rational_nature(Action) :-
    treats_as_object(Action).

harms_rational_nature(Action) :-
    denies_dignity(Action).

%% =============================================================================
%% ETHICAL SCORING: For actions that pass violation checks
%% =============================================================================

% Actions respecting autonomy score high
ethical_score(Action, 0.9) :-
    respects_autonomy(Action),
    promotes_rational_agency(Action),
    \+ violation(Action),
    !.

% Neutral actions (permissible but not meritorious)
ethical_score(Action, 0.5) :-
    \+ violation(Action),
    \+ fulfills_imperfect_duty(Action),
    !.

% Violations score zero
ethical_score(Action, 0.0) :-
    violation(Action),
    !.

%% =============================================================================
%% HELPER PREDICATES (To be unified with Master KG)
%% =============================================================================

% These are abstract predicates that the reasoning engine must instantiate
% with actual case data from the A Posteriori Vault

deceives(Action) :- action_type(Action, deception).
deceives(Action) :- action_type(Action, lie).
deceives(Action) :- action_type(Action, mislead).

breaks_promise(Action) :- action_type(Action, promise_break).

helps_others(Action) :- action_effect(Action, benefit_others).

develops_rational_capacity(Action) :- action_effect(Action, increases_reason).

respects_autonomy(Action) :- 
    \+ coerces(Action, _),
    informed_consent(Action, _).

manipulates(Action, Person) :- 
    action_method(Action, manipulation),
    involves_person(Action, Person).

%% =============================================================================
%% MODULE METADATA (For Master Super KG)
%% =============================================================================

:- meta_predicate 
    module_name(kant),
    module_priority(1.0),  % Highest priority (perfect duties are absolute)
    module_weight(0.25),   % 25% weight in final score
    immutable(true),
    checksum('KANT_V1_CHECKSUM_PLACEHOLDER').

%%% END KANTIAN MODULE %%%
