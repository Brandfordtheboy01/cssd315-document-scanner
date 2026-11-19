"""
Superseded technical-maths presentation deck, retained for reference only.

The app now presents the English-first deck in modules/slides_revised.py.
"""

import streamlit as st

SLIDES = [
    "Slide 1: Title & Overview",
    "Slide 2: The Problem (Mobile Photography)",
    "Slide 3: Step 1 - Corner Detection",
    "Slide 4: Week 3 Theory - Homogeneous Coordinates",
    "Slide 5: Affine (3-Pt) vs. Homography (4-Pt)",
    "Slide 6: The Maths - 8x8 Linear System",
    "Slide 7: Inverse Mapping & Bilinear Interpolation",
    "Slide 8: Clean-up & Shadow Removal",
    "Slide 9: Verification & 20-Photo Benchmark",
    "Slide 10: Live Class Activity",
    "Slide 11: Summary & Viva Cheat Sheet",
]


def _example(title="🧮 Worked example"):
    box = st.container(border=True)
    box.markdown(f"#### {title}")
    return box


# ---------------------------------------------------------------------------
def _slide_1():
    st.markdown("# 📄 DocuScan: Computer Vision Document Scanner")
    st.markdown("### Perspective correction, homography maths and document clean-up")
    st.markdown(
        """
<div style="background-color:#EFF6FF;border-left:6px solid #2563EB;padding:18px;border-radius:6px;margin:20px 0;">
<p style="font-size:1.1rem;color:#1E3A8A;margin:0;"><b>Course:</b> CSSD 315 Computer Graphics</p>
<p style="font-size:1.1rem;color:#1E3A8A;margin:4px 0;"><b>Lecturer:</b> Dr Kwame Assa-Agyei &nbsp;|&nbsp; <b>Institution:</b> GCTU</p>
<p style="font-size:1.1rem;color:#1E3A8A;margin:4px 0;"><b>Group Project, Slot B:</b> Brief 6 (Document Scanner App)</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        r"""
#### 🎯 What the app does
1. Takes a tilted phone photo of a document.
2. Finds the 4 corners of the page automatically.
3. Builds and solves the $8 \times 8$ homography system ourselves with NumPy.
4. Flattens the page with our own inverse mapping and bilinear interpolation.
5. Removes shadows and exports a clean PDF.

Each of these steps gets a worked example with real numbers on the slides that follow.
"""
    )


# ---------------------------------------------------------------------------
def _slide_2():
    st.markdown("## 1. The Problem: Why Document Photos Look Bad")
    st.markdown(
        r"""
Students photograph handouts and notes with their phones all the time, but the photos come out crooked.

### 📐 What goes wrong
1. **Camera tilt:** you rarely hold the phone perfectly flat above the page.
2. **Perspective foreshortening:** the far edge of the page looks smaller than the near edge.
3. **Converging edges:** the page edges are parallel in real life, but in the photo they lean towards each other, like railway tracks meeting in the distance.
4. **Shadows:** your hand, your phone and the room lights throw shadows across the text.
"""
    )
    with _example("🧮 Example: what a tilted A4 page looks like in numbers"):
        st.markdown(
            r"""
A real A4 page is a rectangle. Its top and bottom edges have the **same length**.

In one of our photos, the four corners land at these pixel positions:

| Corner | Pixel position in photo |
| :--- | :--- |
| Top-left | $(120,\ 80)$ |
| Top-right | $(520,\ 110)$ |
| Bottom-right | $(560,\ 600)$ |
| Bottom-left | $(90,\ 560)$ |

- Top edge width: $520 - 120 = 400$ pixels
- Bottom edge width: $560 - 90 = 470$ pixels

The bottom edge looks **70 pixels wider** because it was closer to the camera. That is perspective.
We'll use these same 4 corners on every slide, so you can follow one photo all the way through.
"""
        )
    st.info("Our goal (Brief 6): turn these crooked, shadowy photos into flat, clean, A4-shaped scans.")


# ---------------------------------------------------------------------------
def _slide_3():
    st.markdown("## 2. Step 1: Finding the 4 Corners of the Page")
    st.markdown("**Pipeline:** Raw photo ➜ Greyscale ➜ Blur ➜ Canny edges ➜ Contours ➜ 4 corners")
    st.markdown(
        r"""
1. **Greyscale and Gaussian blur:** remove colour and small noise (like wood grain) so only the big edges stand out.
2. **Canny edge detection:** finds places where brightness changes sharply. It measures the change (the *gradient*) in the $x$ and $y$ directions:
"""
    )
    st.latex(r"\nabla I = \left( \frac{\partial I}{\partial x},\; \frac{\partial I}{\partial y} \right)")
    st.markdown(
        r"In pixels, $\dfrac{\partial I}{\partial x}$ just means **the next pixel's brightness minus this pixel's brightness**."
    )

    with _example("🧮 Example: spotting the edge of the paper"):
        st.markdown(
            r"""
Walk along one row of the photo, from the dark desk onto the white paper. Brightness runs from 0 (black) to 255 (white):

| Pixel $x$ | 0 | 1 | 2 | 3 | 4 | 5 |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| Brightness $I$ | 60 | 62 | 61 | 210 | 212 | 211 |
| what it is | desk | desk | desk | paper | paper | paper |

Now subtract each pixel from the next one:
"""
        )
        st.latex(
            r"\begin{aligned}"
            r"I(1)-I(0) &= 62-60 = 2 \\"
            r"I(2)-I(1) &= 61-62 = -1 \\"
            r"I(3)-I(2) &= 210-61 = \mathbf{149} \\"
            r"I(4)-I(3) &= 212-210 = 2"
            r"\end{aligned}"
        )
        st.markdown(
            r"""
Every change is tiny **except one**: the jump of **149** between pixel 2 and pixel 3.
Our Canny call uses thresholds of 30 and 100. Since $149 > 100$, pixel 3 is marked as a **strong edge**: that's the paper's border.
"""
        )

    st.markdown(
        r"""
3. **Contour approximation (Douglas–Peucker):** joins the edge pixels into an outline, then simplifies it to a shape with **exactly 4 corners**.
4. **Manual fallback:** if a finger or shadow hides an edge, the user drags sliders to place the corners by hand.
"""
    )


# ---------------------------------------------------------------------------
def _slide_4():
    st.markdown("## 3. Week 3 Theory: Homogeneous Coordinates")
    st.markdown("Why do graphics systems add an extra **1** to a 2D point?")

    st.markdown("### ⚠️ The problem with plain 2D")
    st.markdown(r"**Scaling** and **rotation** can be written as $2 \times 2$ matrices:")
    st.latex(r"x' = s_x\,x,\quad y' = s_y\,y \qquad\qquad x' = x\cos\theta - y\sin\theta,\quad y' = x\sin\theta + y\cos\theta")
    st.markdown(r"**Translation** (moving) **can't**. It *adds* a constant, and a $2 \times 2$ matrix can only multiply and add $x$ and $y$ together:")
    st.latex(r"x' = x + t_x, \qquad y' = y + t_y")

    st.markdown("### 💡 The fix: add a 1")
    st.latex(r"(x,\ y) \;\longrightarrow\; \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}")
    st.markdown("Now every transform is a $3 \\times 3$ matrix, translation included.")

    with _example("🧮 Example 1: translation, moving (2, 3) by (4, 1)"):
        st.latex(
            r"\begin{bmatrix} 1 & 0 & 4 \\ 0 & 1 & 1 \\ 0 & 0 & 1 \end{bmatrix}"
            r"\begin{bmatrix} 2 \\ 3 \\ 1 \end{bmatrix} = \;?"
        )
        st.markdown("Multiply **each row** of the matrix by the column, then add:")
        st.latex(
            r"\begin{aligned}"
            r"\text{row 1:}\quad & 1(2) + 0(3) + 4(1) = 2 + 0 + 4 = \mathbf{6} \\"
            r"\text{row 2:}\quad & 0(2) + 1(3) + 1(1) = 0 + 3 + 1 = \mathbf{4} \\"
            r"\text{row 3:}\quad & 0(2) + 0(3) + 1(1) = \mathbf{1}"
            r"\end{aligned}"
        )
        st.markdown(
            r"Answer: $(6,\ 4)$. Check: $2+4=6$ and $3+1=4$ ✅. The **1** at the bottom of the point is what picks up the 4 and the 1 from the last column."
        )

    with _example("🧮 Example 2: scaling (4, 5) by 2 across and 3 up"):
        st.latex(
            r"\begin{bmatrix} 2 & 0 & 0 \\ 0 & 3 & 0 \\ 0 & 0 & 1 \end{bmatrix}"
            r"\begin{bmatrix} 4 \\ 5 \\ 1 \end{bmatrix}"
            r"= \begin{bmatrix} 2(4) \\ 3(5) \\ 1 \end{bmatrix}"
            r"= \begin{bmatrix} 8 \\ 15 \\ 1 \end{bmatrix}"
        )

    with _example("🧮 Example 3: rotating (2, 0) by 30°"):
        st.markdown(r"$\cos 30^\circ = 0.866$ and $\sin 30^\circ = 0.5$")
        st.latex(
            r"\begin{aligned}"
            r"x' &= 2(0.866) - 0(0.5) = \mathbf{1.732} \\"
            r"y' &= 2(0.5) + 0(0.866) = \mathbf{1}"
            r"\end{aligned}"
        )
        st.markdown(r"Answer: $(1.732,\ 1)$, the same worked example as in the Week 3 lecture slides.")

    with _example("🧮 Example 4: why this matters, combining two moves into one"):
        st.markdown(r"First rotate (2, 0) by 30°, **then** move it by (4, 1). Multiply the matrices into one ($T \cdot R$, read right to left):")
        st.latex(
            r"T\,R = \begin{bmatrix} 1 & 0 & 4 \\ 0 & 1 & 1 \\ 0 & 0 & 1 \end{bmatrix}"
            r"\begin{bmatrix} 0.866 & -0.5 & 0 \\ 0.5 & 0.866 & 0 \\ 0 & 0 & 1 \end{bmatrix}"
            r"= \begin{bmatrix} 0.866 & -0.5 & 4 \\ 0.5 & 0.866 & 1 \\ 0 & 0 & 1 \end{bmatrix}"
        )
        st.latex(
            r"\begin{aligned}"
            r"x' &= 0.866(2) - 0.5(0) + 4 = \mathbf{5.732} \\"
            r"y' &= 0.5(2) + 0.866(0) + 1 = \mathbf{2}"
            r"\end{aligned}"
        )
        st.markdown(r"Check: the rotation gave $(1.732, 1)$, and adding $(4, 1)$ gives $(5.732, 2)$ ✅. **One** matrix did both jobs.")


# ---------------------------------------------------------------------------
def _slide_5():
    st.markdown("## 4. Affine (3 Points) vs. Homography (4 Points)")
    st.markdown("**Course requirement 4:** show why an affine warp is not enough for a phone photo.")

    c1, c2 = st.columns(2)
    with c1:
        st.error("❌ 3-point affine transform")
        st.latex(r"\begin{bmatrix} a_{11} & a_{12} & t_x \\ a_{21} & a_{22} & t_y \\ 0 & 0 & 1 \end{bmatrix}")
        st.markdown(
            r"""
- 6 unknowns, so **3 points** are enough.
- Bottom row is always $[0,\ 0,\ 1]$, so $w'$ is always 1.
- Parallel lines **stay parallel**.
"""
        )
    with c2:
        st.success("✅ 4-point homography")
        st.latex(r"\begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix}")
        st.markdown(
            r"""
- 8 unknowns, so it needs **4 points**.
- Bottom row can change, so $w'$ changes from point to point.
- Dividing by $w'$ lets parallel lines **meet**, just like in a photo.
"""
        )

    with _example("🧮 Example 1: how dividing by w′ creates perspective"):
        st.markdown(r"Take a simple homography whose only bottom-row change is $h_{31} = 0.001$:")
        st.latex(r"H = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0.001 & 0 & 1 \end{bmatrix} \quad\Rightarrow\quad w' = 0.001\,x + 1")
        st.markdown(r"Now push two **parallel horizontal lines** (at $y = 50$ and $y = 150$) through it:")
        st.markdown(
            r"""
| Point | $w' = 0.001x + 1$ | New point $= (x/w',\ y/w')$ |
| :--- | :-: | :--- |
| $(100,\ 50)$ | $1.1$ | $(90.91,\ 45.45)$ |
| $(100,\ 150)$ | $1.1$ | $(90.91,\ 136.36)$ |
| $(500,\ 50)$ | $1.5$ | $(333.33,\ 33.33)$ |
| $(500,\ 150)$ | $1.5$ | $(333.33,\ 100.00)$ |
"""
        )
        st.markdown(
            r"""
Gap between the two lines:
- at the left: $136.36 - 45.45 = \mathbf{90.91}$
- at the right: $100.00 - 33.33 = \mathbf{66.67}$

The gap **shrinks**, so the lines are no longer parallel: they lean towards each other like railway tracks.
With affine, $w'$ is always 1, so the gap would stay the same everywhere. **Affine can't make lines meet, and it can't un-meet them either.**
"""
        )

    with _example("🧮 Example 2: affine on our real photo, using only 3 corners"):
        st.markdown(
            r"""
We solve an affine transform from **3** of our photo corners (TL, TR, BL) and ask it to send them to the A4 corners.
Then we check where the **4th corner**, bottom-right $(560,\ 600)$, ends up:
"""
        )
        st.latex(
            r"\begin{bmatrix} 0.9953 & 0.0622 & -124.42 \\ -0.0778 & 1.0368 & -73.61 \\ 0 & 0 & 1 \end{bmatrix}"
            r"\begin{bmatrix} 560 \\ 600 \\ 1 \end{bmatrix}"
            r"= \begin{bmatrix} 470.30 \\ 504.92 \\ 1 \end{bmatrix}"
        )
        st.markdown(
            r"""
It **should** land on $(400,\ 500)$, but it lands on $(470.30,\ 504.92)$: about **70 pixels off**.
That's the 70 extra pixels of bottom edge we measured on Slide 2. Affine can't remove them, so the scan comes out skewed.
The homography on the next slide puts all 4 corners exactly where they belong.
"""
        )


# ---------------------------------------------------------------------------
def _slide_6():
    st.markdown("## 5. The Maths: Building the 8×8 Linear System")
    st.markdown(
        r"We need the 8 unknown numbers in $H$, and we find them **without** OpenCV's `findHomography`. "
        r"Each photo corner $(x, y)$ must land on a page corner $(u, v)$:"
    )
    st.latex(
        r"u = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + 1}, \qquad "
        r"v = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + 1}"
    )
    st.markdown(
        r"($h_{33}$ is set to 1. Scaling all of $H$ by the same number gives the same picture, so we're free to pick it.) "
        r"Multiply both sides by the bottom of the fraction and move everything with an $h$ to the left. Each corner gives **two equations**:"
    )
    st.latex(r"h_{11}x + h_{12}y + h_{13} - h_{31}\,ux - h_{32}\,uy = u")
    st.latex(r"h_{21}x + h_{22}y + h_{23} - h_{31}\,vx - h_{32}\,vy = v")
    st.markdown(r"4 corners × 2 equations = **8 equations** for **8 unknowns**, written as $\mathbf{A}\,\mathbf{h} = \mathbf{b}$.")

    with _example("🧮 Example: solving H for our real photo"):
        st.markdown(
            r"""
**Step 1: list the 4 corner pairs.** The photo corners come from Slide 2, and the target is a 400 × 500 page:

| Corner | Photo $(x, y)$ | Page $(u, v)$ |
| :--- | :--- | :--- |
| TL | $(120,\ 80)$ | $(0,\ 0)$ |
| TR | $(520,\ 110)$ | $(400,\ 0)$ |
| BR | $(560,\ 600)$ | $(400,\ 500)$ |
| BL | $(90,\ 560)$ | $(0,\ 500)$ |

**Step 2: build the 2 rows for one corner.** Take TR, where $x = 520,\ y = 110,\ u = 400,\ v = 0$:
"""
        )
        st.latex(
            r"\begin{aligned}"
            r"-u\,x &= -400 \times 520 = -208\,000 \\"
            r"-u\,y &= -400 \times 110 = -44\,000 \\"
            r"-v\,x &= -0 \times 520 = 0, \qquad -v\,y = 0"
            r"\end{aligned}"
        )
        st.latex(
            r"\text{Row 3: } [\,520,\ 110,\ 1,\ 0,\ 0,\ 0,\ -208000,\ -44000\,] \;=\; 400"
        )
        st.latex(
            r"\text{Row 4: } [\,0,\ 0,\ 0,\ 520,\ 110,\ 1,\ 0,\ 0\,] \;=\; 0"
        )
        st.markdown(r"**Step 3: do the same for all 4 corners** to get the full system:")
        st.latex(
            r"\underbrace{\begin{bmatrix}"
            r"120 & 80 & 1 & 0 & 0 & 0 & 0 & 0 \\"
            r"0 & 0 & 0 & 120 & 80 & 1 & 0 & 0 \\"
            r"520 & 110 & 1 & 0 & 0 & 0 & -208000 & -44000 \\"
            r"0 & 0 & 0 & 520 & 110 & 1 & 0 & 0 \\"
            r"560 & 600 & 1 & 0 & 0 & 0 & -224000 & -240000 \\"
            r"0 & 0 & 0 & 560 & 600 & 1 & -280000 & -300000 \\"
            r"90 & 560 & 1 & 0 & 0 & 0 & 0 & 0 \\"
            r"0 & 0 & 0 & 90 & 560 & 1 & -45000 & -280000"
            r"\end{bmatrix}}_{\mathbf{A}}"
            r"\begin{bmatrix} h_{11} \\ h_{12} \\ h_{13} \\ h_{21} \\ h_{22} \\ h_{23} \\ h_{31} \\ h_{32} \end{bmatrix}"
            r"= \underbrace{\begin{bmatrix} 0 \\ 0 \\ 400 \\ 0 \\ 400 \\ 500 \\ 0 \\ 500 \end{bmatrix}}_{\mathbf{b}}"
        )
        st.markdown(r"**Step 4: solve it** with `h = np.linalg.solve(A, b)`, then put $h_{33} = 1$ back:")
        st.latex(
            r"H = \begin{bmatrix} 1.0328 & 0.0646 & -129.10 \\ -0.0939 & 1.2526 & -88.93 \\ -0.0000064 & 0.00037268 & 1 \end{bmatrix}"
        )
        st.markdown(r"**Step 5: check it.** Send TR $(520,\ 110)$ through $H$:")
        st.latex(
            r"\begin{aligned}"
            r"u' &= 1.0328(520) + 0.0646(110) - 129.10 = 415.07 \\"
            r"v' &= -0.0939(520) + 1.2526(110) - 88.93 = 0 \\"
            r"w' &= -0.0000064(520) + 0.00037268(110) + 1 = 1.0377 \\[4pt]"
            r"u &= \frac{415.07}{1.0377} = \mathbf{400}, \qquad v = \frac{0}{1.0377} = \mathbf{0} \;\; \checkmark"
            r"\end{aligned}"
        )
        st.markdown(r"TR lands exactly on $(400,\ 0)$. The other 3 corners land exactly on their page corners too.")


# ---------------------------------------------------------------------------
def _slide_7():
    st.markdown("## 6. Flattening the Image: Inverse Mapping & Bilinear Interpolation")

    st.markdown("### 🚫 Why not forward mapping?")
    st.markdown(r"Forward mapping takes each **photo** pixel and pushes it onto the page with $H$. That leaves gaps.")
    with _example("🧮 Example: forward mapping leaves holes"):
        st.markdown(
            r"""
Say the page is **2× bigger** than the photo region, so each photo pixel moves to $2x$:

| Photo pixel $x$ | 0 | 1 | 2 | 3 |
| :--- | :-: | :-: | :-: | :-: |
| Lands on page pixel $2x$ | 0 | 2 | 4 | 6 |

Page pixels **1, 3 and 5 never get a colour**, so they show up as holes. Real homographies stretch some areas more than others, which produces cracks all over the scan.
"""
        )

    st.markdown("### 🔄 The fix: inverse mapping")
    st.markdown(
        r"Go through **every page pixel** $(u, v)$ and ask: *which photo pixel does this come from?* Answer it with the inverse matrix $H^{-1}$:"
    )
    st.latex(
        r"\begin{bmatrix} x' \\ y' \\ w' \end{bmatrix} = H^{-1} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix},"
        r"\qquad x = \frac{x'}{w'}, \qquad y = \frac{y'}{w'}"
    )
    with _example("🧮 Example: where does page pixel (200, 250) come from?"):
        st.markdown(r"Using $H^{-1}$ of the matrix from the last slide:")
        st.latex(
            r"H^{-1}\begin{bmatrix} 200 \\ 250 \\ 1 \end{bmatrix} = \begin{bmatrix} 287.81 \\ 284.77 \\ 0.8957 \end{bmatrix}"
            r"\quad\Rightarrow\quad x = \frac{287.81}{0.8957} = \mathbf{321.32}, \qquad y = \frac{284.77}{0.8957} = \mathbf{317.92}"
        )
        st.markdown(
            r"""
So page pixel $(200,\ 250)$ takes its colour from photo position $(321.32,\ 317.92)$.
Sanity check: page corner $(0,\ 0)$ maps back to $(120,\ 80)$, the photo's top-left corner ✅.

Because we visit **every** page pixel, nothing is left empty. But $321.32$ isn't a whole pixel, so which colour do we take?
"""
        )

    st.markdown("### 🎨 Bilinear interpolation")
    st.markdown(
        r"Blend the **4 nearest pixels**. The closer a pixel is, the more of its colour we use. "
        r"$dx$ and $dy$ are the decimal parts of the position:"
    )
    st.latex(r"I = (1-dx)(1-dy)\,I_a + dx(1-dy)\,I_b + (1-dx)\,dy\,I_c + dx\,dy\,I_d")
    st.markdown(r"$I_a$ = top-left, $I_b$ = top-right, $I_c$ = bottom-left, $I_d$ = bottom-right neighbour.")
    with _example("🧮 Example: the colour at (321.32, 317.92)"):
        st.markdown(
            r"""
**Step 1: find the 4 neighbours and the decimal parts.**
- $x = 321.32$, so the neighbours are columns 321 and 322, and $dx \approx 0.32$
- $y = 317.92$, so the neighbours are rows 317 and 318, and $dy \approx 0.92$

Suppose the 4 neighbours have these brightness values (the top two are paper, the bottom two are ink):

| | column 321 | column 322 |
| :--- | :-: | :-: |
| **row 317** | $I_a = 200$ | $I_b = 180$ |
| **row 318** | $I_c = 60$ | $I_d = 40$ |

**Step 2: work out each weight.**
"""
        )
        st.latex(
            r"\begin{aligned}"
            r"(1-dx)(1-dy) &= 0.68 \times 0.08 = 0.0544 \\"
            r"dx\,(1-dy) &= 0.32 \times 0.08 = 0.0256 \\"
            r"(1-dx)\,dy &= 0.68 \times 0.92 = 0.6256 \\"
            r"dx\,dy &= 0.32 \times 0.92 = 0.2944 \\"
            r"\text{total} &= 1.0000 \;\; \checkmark"
            r"\end{aligned}"
        )
        st.markdown(r"**Step 3: multiply and add.**")
        st.latex(
            r"\begin{aligned}"
            r"I &= 0.0544(200) + 0.0256(180) + 0.6256(60) + 0.2944(40) \\"
            r"  &= 10.88 + 4.61 + 37.54 + 11.78 = \mathbf{64.8}"
            r"\end{aligned}"
        )
        st.markdown(
            r"""
$dy = 0.92$ means the point is very close to the **bottom** (ink) row, so the answer, 64.8, sits close to the ink values (60 and 40).
That smooth blending is why letters come out clean instead of jagged.
"""
        )


# ---------------------------------------------------------------------------
def _slide_8():
    st.markdown("## 7. Clean-up: Shadow Removal & Scan Look")
    st.markdown("After flattening, the page is the right shape but may still be dark or shadowy. We fix that in 3 ways.")

    st.markdown("### 1. Shadow removal (dividing out the lighting)")
    st.markdown(
        r"A very strong blur ($\sigma = 35$) smudges away the text and leaves only the **lighting**: how bright each area of the page is. "
        r"Dividing by that lighting evens out the whole page:"
    )
    st.latex(r"I_{clean} = \frac{I_{pixel}}{I_{blurred}} \times 255")
    with _example("🧮 Example: one bright area, one shadowed area"):
        st.markdown(
            r"""
The left half of the page is well lit (blurred brightness **220**). The right half is under a shadow (blurred brightness **110**).

| Pixel | Brightness | Blurred lighting | Calculation | Result |
| :--- | :-: | :-: | :--- | :-: |
| paper, bright side | 220 | 220 | $220 / 220 \times 255$ | **255** |
| paper, shadow side | 110 | 110 | $110 / 110 \times 255$ | **255** |
| ink, bright side | 80 | 220 | $80 / 220 \times 255$ | **92.7** |
| ink, shadow side | 40 | 110 | $40 / 110 \times 255$ | **92.7** |

Before, paper was 220 on one side and 110 on the other. **After, both are 255 (pure white)**, and both ink pixels come out at the same 92.7. The shadow is gone.
"""
        )

    st.markdown("### 2. Adaptive threshold (photocopy look)")
    st.markdown(
        r"Every pixel becomes pure black or pure white. Instead of one cut-off for the whole page, each pixel gets its **own** cut-off: "
        r"the (weighted) average of the pixels around it, minus a constant $C = 10$."
    )
    with _example("🧮 Example: one cut-off vs. a local cut-off in the shadow"):
        st.markdown(
            r"""
In the shadowed area, paper is 110 and ink is 40.

**One global cut-off of 128:**
- paper $110 < 128$ ➜ **black** ❌ (the shadowed paper turns into a black blob)

**Adaptive (local) cut-off:** the area around it averages 110, so the cut-off is $110 - 10 = 100$.
- paper $110 > 100$ ➜ **white** ✅
- ink $40 < 100$ ➜ **black** ✅
"""
        )

    st.markdown("### 3. Colour enhancement (CLAHE in LAB colour space)")
    st.markdown(
        r"For colour handouts we convert to LAB, which separates **L = lightness** from the colour channels. "
        r"We boost contrast **only on L**, so the page gets sharper while the ink keeps its colour."
    )


# ---------------------------------------------------------------------------
def _slide_9():
    st.markdown("## 8. Checking Our Work: OpenCV Comparison & 20-Photo Test")
    st.markdown(
        r"""
### 🔬 1. Compare with OpenCV
- We flatten the same photo twice: once with **our own code** and once with OpenCV's `cv2.warpPerspective`.
- We subtract the two results pixel by pixel: $\text{difference} = |\,\text{ours} - \text{OpenCV}\,|$.
- We average those differences over every pixel. An average close to **0** (out of 255) means our maths matches OpenCV's.
- The **heat map** colours each pixel by its difference, so any problem area stands out.
"""
    )
    with _example("🧮 Example: reading the difference"):
        st.markdown(
            r"""
| Pixel | Ours | OpenCV | Difference |
| :--- | :-: | :-: | :-: |
| A | 200 | 200 | 0 |
| B | 64 | 65 | 1 |
| C | 255 | 255 | 0 |
| D | 37 | 37 | 0 |

Mean difference $= (0 + 1 + 0 + 0) / 4 = 0.25$ out of 255. That's about 0.1%, too small to see.
*(Illustrative numbers. Open the Interactive Scanner page to get the real value for any photo.)*
"""
        )
    st.markdown(
        r"""
---
### 📊 2. The 20-photo benchmark
The handbook asks for 20 test photos covering different angles, lighting and backgrounds. Our test set has 4 groups:
1. Straight and slightly tilted pages
2. Steep perspective (strong keystone effect)
3. Shadows and low light
4. Busy or low-contrast backgrounds
"""
    )
    st.latex(r"\text{Success rate} = \frac{\text{photos scanned correctly}}{20} \times 100\%")
    st.markdown(r"Example: if 17 of 20 scan correctly, $17/20 \times 100\% = 85\%$. Run the **Course Benchmark** page to get the real figure.")


# ---------------------------------------------------------------------------
def _slide_10():
    st.markdown("## 9. Live Demo & Class Activity")
    st.markdown(
        r"""
The handbook says:
> *"Classmates photograph a page with their phones; the group scans the photos live."*

### 🌐 How it works in class
- The app runs on the laptop and can be opened from any phone on the **same Wi-Fi**, using the laptop's network address (for example `http://192.168.x.x:8501`).
- **Steps for classmates:**
  1. Join the class Wi-Fi.
  2. Open the link in the phone browser.
  3. Choose **"Use Live Camera"** and photograph any handout.
  4. Watch the projector as the page is detected, flattened and cleaned, then download the PDF.
"""
    )


# ---------------------------------------------------------------------------
def _slide_11():
    st.markdown("## 10. Summary & Viva Cheat Sheet")
    st.markdown(
        r"""
| Question | Simple answer | Number to quote |
| :--- | :--- | :--- |
| **Why homogeneous coordinates?** | Adding a 1 lets translation be a matrix multiplication, so every transform is a 3×3 matrix and they can be combined. | $(2,3)$ moved by $(4,1)$ gives $(6,4)$ |
| **Why 8 equations?** | $H$ has 9 numbers. We fix $h_{33} = 1$, which leaves 8 unknowns. Each corner gives 2 equations, so 4 corners give 8. | TR row: $[520, 110, 1, 0, 0, 0, -208000, -44000] = 400$ |
| **Why doesn't affine work?** | Its bottom row is fixed at $[0, 0, 1]$, so $w' = 1$ and parallel lines stay parallel. A tilted photo needs lines that meet. | 4th corner lands ~70 px off: $(470, 505)$ instead of $(400, 500)$ |
| **What does dividing by $w'$ do?** | Points with a bigger $w'$ get pulled in more, which is what makes far things look small. | Gap shrank from 90.91 to 66.67 |
| **Why inverse mapping?** | Forward mapping leaves holes. Inverse mapping visits every page pixel and looks back into the photo. | Page $(200, 250)$ ← photo $(321.32, 317.92)$ |
| **What does bilinear interpolation do?** | Blends the 4 nearest pixels, weighted by how close they are. | Weights $0.0544 + 0.0256 + 0.6256 + 0.2944 = 1$, giving 64.8 |
| **How does shadow removal work?** | Divide each pixel by the blurred lighting, so bright and shadowed paper both become white. | $220/220$ and $110/110$ both give 255 |
"""
    )


_RENDERERS = [
    _slide_1, _slide_2, _slide_3, _slide_4, _slide_5, _slide_6,
    _slide_7, _slide_8, _slide_9, _slide_10, _slide_11,
]


def render_slides():
    st.markdown('<p class="main-header">🖥️ Presentation Slide Deck</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">CSSD 315 Computer Graphics • Brief 6: Document Scanner App • Dr Kwame Assa-Agyei</p>',
        unsafe_allow_html=True,
    )

    if "slide_idx" not in st.session_state:
        st.session_state.slide_idx = 0

    def _go(delta):
        st.session_state.slide_idx = max(0, min(len(SLIDES) - 1, st.session_state.slide_idx + delta))

    nav1, nav2, nav3 = st.columns([1, 4, 1])
    with nav1:
        st.button("⬅️ Previous", on_click=_go, args=(-1,), use_container_width=True,
                  disabled=st.session_state.slide_idx == 0)
    with nav2:
        choice = st.selectbox("Jump to slide:", SLIDES, index=st.session_state.slide_idx,
                              label_visibility="collapsed")
        if SLIDES.index(choice) != st.session_state.slide_idx:
            st.session_state.slide_idx = SLIDES.index(choice)
            st.rerun()
    with nav3:
        st.button("Next ➡️", on_click=_go, args=(1,), use_container_width=True,
                  disabled=st.session_state.slide_idx == len(SLIDES) - 1)

    idx = st.session_state.slide_idx
    st.progress((idx + 1) / len(SLIDES), text=f"Slide {idx + 1} of {len(SLIDES)}")
    st.markdown("---")
    _RENDERERS[idx]()
