% Confucian Ethics Rules
% Five Relationships & Ren (benevolence)

% The Five Relationships
relationship(ruler, subject).
relationship(father, son).
relationship(husband, wife).
relationship(elder_sibling, younger_sibling).
relationship(friend, friend).

% Filial Piety (孝 xiào)
virtue(filial_piety).
filial_piety_requires(respect_parents).
filial_piety_requires(care_for_elders).
filial_piety_requires(honor_ancestors).

violation(Action) :-
    action_toward(Action, parent),
    disrespectful(Action).

% Ren (仁) - Benevolence/Humaneness
virtue(ren).
ren_requires(compassion).
ren_requires(empathy).
ren_requires(humaneness).

ethical(Action) :-
    shows_compassion(Action),
    promotes_harmony(Action).

% Li (禮) - Proper Conduct/Ritual
virtue(li).
li_requires(proper_etiquette).
li_requires(social_roles).

% Yi (義) - Righteousness
virtue(yi).
yi_requires(moral_correctness).
yi_requires(duty_to_society).

% Reciprocity (Shu 恕) - The Silver Rule
violation(Action) :-
    would_not_want_done_to_self(Action).

% Social Harmony
promotes_harmony(Action) :-
    action_type(Action, mediation).

promotes_harmony(Action) :-
    action_type(Action, reconciliation).

violation(Action) :-
    disrupts_social_harmony(Action).

% Helper predicates
shows_compassion(help_others).
shows_compassion(comfort_suffering).
shows_compassion(support_weak).

disrespectful(insult).
disrespectful(ignore_elder).
disrespectful(dishonor).

would_not_want_done_to_self(Action) :-
    harmful(Action),
    not justified(Action).
