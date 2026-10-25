# meat-oracle

**The Meat Oracle** — a single-page grilling calculator that divines how much meat to buy for a cookout, then suggests what to cook with it.

No build step, no dependencies. One self-contained `index.html`: markup, styles, SVG artwork, and logic all inline.

## What it does

You tell it who's coming and the rest follows:

- **The Gathering** — counts of men, women, and kids, each with an average appetite slider. Appetite only nudges the total (~15% each way), so a crowd of carnivores buys a bit more, not double. The slider is the group average, so a mixed group (say two big eaters and one regular) just lands near the middle. Kids use an average-age slider (2 to 17) that scales the portion smoothly, so in-between ages and mixed-age kids both work: a 4 and a 14 average to about 9.
- **The Offerings** — choice and balance in one control. Each protein (beef, pork, chicken, sausage, fish, shellfish, paneer, tofu) is a slider: at 0 it's off, drag it up to add it and the further you push the bigger its share. Shares snap to 5% and sum to 100. The slider handle is the critter itself (beef is a cow, pork a pig, and so on); the people sliders are a man, a woman, and a child. Because it's a fixed list, the layout never grows or scrolls no matter how many you pick.
- **The Flame** — charcoal, gas, smoker, or electric. This doesn't change how much people eat; it shapes the cooking tips and nudges the smoker number up for the long low-and-slow shrink.
- **Sides toggle** — trims the meat by a quarter when there's a real spread of sides.

Output is total **raw** pounds to buy and a per-protein breakdown rounded to a tenth of a pound, shown side by side. A **View the recipes** button opens a panel (a side modal on desktop, a bottom sheet on mobile) with two recipes per protein for the selected grill (8 proteins x 4 grills, 64 picks). Each links to the original recipe, plus a "similar on Google" link built from the dish and grill. The picks were researched on the web in Oct 2026 from publishers like Serious Eats, America's Test Kitchen, NYT Cooking, Food Network and AmazingRibs. They are curated and baked into the page (it is a static site, so there is no live search). Electric, paneer-smoker and shellfish picks lean on smaller blogs where the big publishers had little.

## How the math works

Each eater gets a target of **cooked** edible meat (a regular man ~0.5 lb, a regular woman a bit less, a kid scaled by age), nudged about 15% each way by the average appetite slider. That cooked target is split across the proteins by the share you give each one (you fill a 100% plate in 5% steps, and it locks at full), then grossed up to raw buying weight using a per-protein yield factor that accounts for cooking shrink plus bone and shell waste. Shellfish needs the most raw weight (mostly shell); sausage, paneer, and tofu the least. These are grill-day rules of thumb, not lab figures.

## Design

Styled as a mystic linocut broadside: a single dark ink tone printed on kraft paper, hand-drawn SVG artwork (an all-seeing eye radiating sunbeams) run through an SVG displacement filter so the edges break like carved block-print ink. Woodblock display type (Rye) over typewriter body (Special Elite).

On desktop it's a no-scroll, three-pane dashboard (20/30/50): the family, the offerings (proteins, sides), and the verdict with the grill choice. Recipes open in a side modal (bottom sheet on mobile). On narrow screens the panes stack into a single column.

## Run it

Open `index.html` in a browser. That's the whole thing.

## Deploy

Netlify, base directory `meat-oracle`, publish `.` — static, no build command. See `netlify.toml`.
