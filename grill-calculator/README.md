# grill-calculator

**The Meat Oracle** — a single-page grilling calculator that divines how much meat to buy for a cookout, then suggests what to cook with it.

No build step, no dependencies. One self-contained `index.html`: markup, styles, SVG artwork, and logic all inline.

## What it does

You tell it who's coming and the rest follows:

- **The Gathering** — counts of men, women, and kids, each with an average appetite slider. Appetite only nudges the total (~15% each way), so a crowd of carnivores buys a bit more, not double. The slider is the group average, so a mixed group (say two big eaters and one regular) just lands near the middle. Kids use an average-age slider (2 to 17) that scales the portion smoothly, so in-between ages and mixed-age kids both work: a 4 and a 14 average to about 9.
- **The Offerings** — pick your proteins (beef, pork, chicken, sausage, fish, shellfish, paneer, tofu).
- **The Balance** — a share slider per chosen protein, even by default. Drag to favor one. Shares are portions of the meal; raw buy-weights still differ because bonier or shell proteins need more weight to hit the same cooked amount.
- **The Flame** — charcoal, gas, smoker, or electric. This doesn't change how much people eat; it shapes the cooking tips and nudges the smoker number up for the long low-and-slow shrink.
- **Sides toggle** — trims the meat by a quarter when there's a real spread of sides.

Output is total **raw** pounds to buy, a per-protein breakdown rounded to a tenth of a pound, and a recipe suggestion per protein (low-and-slow cuts when a smoker is selected), each linking out to a recipe search. The balance sliders set each protein's share in 5% steps.

## How the math works

Each eater gets a target of **cooked** edible meat (a regular man ~0.5 lb, a regular woman a bit less, a kid scaled by age), nudged about 15% each way by the average appetite slider. That cooked target is split across the chosen proteins by the balance sliders (even by default), then grossed up to raw buying weight using a per-protein yield factor that accounts for cooking shrink plus bone and shell waste. Shellfish needs the most raw weight (mostly shell); sausage, paneer, and tofu the least. These are grill-day rules of thumb, not lab figures.

## Design

Styled as a mystic linocut broadside: a single dark ink tone printed on kraft paper, hand-drawn SVG artwork (an all-seeing eye radiating sunbeams) run through an SVG displacement filter so the edges break like carved block-print ink. Woodblock display type (Rye) over typewriter body (Special Elite).

## Run it

Open `index.html` in a browser. That's the whole thing.

## Deploy

Netlify, base directory `grill-calculator`, publish `.` — static, no build command. See `netlify.toml`.
