// cosmic.js — Moon phase + Mercury retrograde logic
// Ported from mercury_check.py. No dependencies.

const MOON_PHASES = [
  { threshold: 0.0625, emoji: '🌑', label: 'New Moon',         guidance: 'Fresh starts encouraged. Risky deploys discouraged.' },
  { threshold: 0.1875, emoji: '🌒', label: 'Waxing Crescent',  guidance: 'Good energy for new features.' },
  { threshold: 0.3125, emoji: '🌓', label: 'First Quarter',    guidance: 'Build momentum. Ship incrementally.' },
  { threshold: 0.4375, emoji: '🌔', label: 'Waxing Gibbous',   guidance: 'Refinement phase. Good for bug fixes.' },
  { threshold: 0.5625, emoji: '🌕', label: 'Full Moon',        guidance: 'Emotions are high. Review carefully. Maybe hydrate.' },
  { threshold: 0.6875, emoji: '🌖', label: 'Waning Gibbous',   guidance: 'Integration and reflection. Good for docs.' },
  { threshold: 0.8125, emoji: '🌗', label: 'Last Quarter',     guidance: 'Release old patterns. Refactor with intention.' },
  { threshold: 0.9375, emoji: '🌘', label: 'Waning Crescent',  guidance: 'Rest phase. Avoid major architecture decisions.' },
  { threshold: 1.0,    emoji: '🌑', label: 'New Moon',         guidance: 'Fresh starts encouraged. Risky deploys discouraged.' },
];

// Known Mercury retrograde windows — extend each year
const RETROGRADE_PERIODS = [
  ['2025-03-15', '2025-04-07'],
  ['2025-07-18', '2025-08-11'],
  ['2025-11-09', '2025-11-29'],
  ['2026-01-10', '2026-01-31'],
  ['2026-05-05', '2026-05-28'],
  ['2026-09-04', '2026-09-26'],
];

// Approval probability weights by moon phase
const COSMOS_WEIGHTS = {
  'Full Moon':        0.70,
  'Waxing Gibbous':   0.65,
  'First Quarter':    0.60,
  'Waxing Crescent':  0.60,
  'New Moon':         0.50,
  'Waning Gibbous':   0.45,
  'Last Quarter':     0.40,
  'Waning Crescent':  0.40,
};

function getMoonPhase(date = new Date()) {
  const knownNewMoon = new Date('2000-01-06');
  const daysSince = (date - knownNewMoon) / (1000 * 60 * 60 * 24);
  const cyclePosition = ((daysSince % 29.53) + 29.53) % 29.53 / 29.53;
  return MOON_PHASES.find(p => cyclePosition < p.threshold) || MOON_PHASES[0];
}

function getMercuryStatus(date = new Date()) {
  const target = date.toISOString().slice(0, 10);
  for (const [start, end] of RETROGRADE_PERIODS) {
    if (target >= start && target <= end) {
      const endDate = new Date(end);
      const daysUntilDirect = Math.ceil((endDate - date) / (1000 * 60 * 60 * 24));
      return { retrograde: true, endsOn: end, daysUntilDirect };
    }
  }
  return { retrograde: false, endsOn: null, daysUntilDirect: null };
}

function getCosmicStatus(date = new Date()) {
  const moon = getMoonPhase(date);
  const mercury = getMercuryStatus(date);
  return {
    moonEmoji: moon.emoji,
    moonLabel: moon.label,
    moonGuidance: moon.guidance,
    mercuryRetrograde: mercury.retrograde,
    retrogradeEndsOn: mercury.endsOn,
    daysUntilDirect: mercury.daysUntilDirect,
    mergeBlocked: mercury.retrograde,
  };
}

function cosmosDecides(status = getCosmicStatus()) {
  let weight = COSMOS_WEIGHTS[status.moonLabel] ?? 0.5;
  if (status.mercuryRetrograde) weight = Math.max(0, weight - 0.15);

  const approved = Math.random() < weight;
  const retroNote = status.mercuryRetrograde ? ', Mercury retrograde' : '';
  const note = `The cosmos (${status.moonEmoji} ${status.moonLabel}${retroNote}) `
    + `${approved ? 'favor' : 'do not favor'} this merge.`;

  return { approved, state: approved ? 'APPROVE' : 'REQUEST_CHANGES', note };
}
