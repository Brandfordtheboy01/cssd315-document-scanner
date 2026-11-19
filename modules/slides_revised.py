"""English-first, presenter-friendly slides for the CSSD 315 scanner project."""

import streamlit as st


SLIDES = [
    "1. DocuScan: a practical document scanner",
    "2. The everyday problem",
    "3. What the app does",
    "4. Finding the page in a photo",
    "5. Making a flat scan from an angled photo",
    "6. Building a readable image",
    "7. How the project is put together",
    "8. Testing the scanner fairly",
    "9. Demonstration for the class",
    "10. What works well and what can be difficult",
    "11. Lessons learned and future improvements",
    "12. Conclusion",
]


_SLIDE_CONTENT = [
    (
        "DocuScan: A Practical Document Scanner",
        """
### CSSD 315 Computer Graphics — Group Project, Brief 6

DocuScan is a browser-based tool that turns a photograph of a paper document
into a cleaner, easier-to-read scan. It is designed for ordinary situations:
someone has a phone, a page of notes, and no flatbed scanner nearby.

This presentation explains the project in everyday language. It follows the
experience from taking a photograph through to saving the finished document,
and describes how we built and tested the application without relying on
equations to tell the story.
""",
    ),
    (
        "The Everyday Problem",
        """
Photographing a page seems simple, but the result is often difficult to use.
The phone may be held at an angle, the page may be closer to one side of the
camera, and the room may not be evenly lit. These conditions can make a
rectangular sheet look slanted or uneven.

Shadows from a hand or phone can hide words. A patterned desk can make the
page boundary hard to distinguish. Small movements can soften letters, and
the image may include a large area of background that is not part of the
document.

The goal is not merely to save the photograph. The goal is to make the page
look more like a clean scan while keeping its important content visible.
""",
    ),
    (
        "What the App Does",
        """
The user can provide an image by uploading a photograph, taking one with a
connected camera, or choosing a sample image supplied with the project. The
app then looks for the document, straightens it, and offers image-cleanup
options.

If automatic page detection is uncertain, the user can adjust the page
corners manually. This matters because a fully automatic system cannot
reliably interpret every photograph, especially when a finger covers an
edge or the page blends into its background.

When the result is ready, the user can inspect it and download a clean image
or a PDF. The project also includes a batch-testing view for trying the
scanner on a collection of varied sample photographs.
""",
    ),
    (
        "Finding the Page in a Photo",
        """
Before the page can be straightened, the app needs to estimate where the
page begins and ends. It first simplifies the photograph so that differences
in brightness are easier to inspect. A small amount of smoothing reduces
visual distractions such as fine texture in a desk or camera noise.

The detector then looks for strong boundaries and groups nearby boundary
segments into outlines. It gives preference to an outline that resembles a
four-sided sheet of paper. Once it has a likely page outline, it identifies
the four corners in a consistent order.

Detection is an informed guess, not a guarantee. A busy background, weak
contrast, a curled page, or a cropped corner can confuse it. That is why the
app includes a manual corner-adjustment option instead of forcing users to
accept a poor automatic result.
""",
    ),
    (
        "Making a Flat Scan from an Angled Photo",
        """
A page photographed from above at an angle does not look rectangular in the
image. Its far edge may appear shorter, and its sides may seem to lean
towards one another. This is a normal effect of viewing a flat object from a
particular position; it does not mean that the paper itself is misshapen.

DocuScan uses the four detected page corners as landmarks. It compares their
positions in the photograph with the corners of a flat output page, then
works out how the image should be remapped so the photographed page fits
that flat shape.

The project implements this perspective correction itself. In plain terms,
it calculates where the photographed content belongs on the finished page,
rather than simply rotating or stretching the entire photo. This is why it
can correct perspective that a basic rotate-and-crop operation would leave
behind.
""",
    ),
    (
        "Building a Readable Image",
        """
After the page has been straightened, the app can improve how it looks.
Grayscale mode removes colour when colour is not useful. A black-and-white
option can make printed text stand out, while colour enhancement is available
when the original colours should be retained.

Lighting is another common problem. A shadow may make one part of a page
look much darker than another. The shadow-removal filter estimates the broad
lighting pattern and uses it to balance the page. Because this is a basic
image-processing method, it can improve uneven lighting but cannot restore
details that were completely hidden or lost.

The app also samples image colours smoothly when it resizes and reshapes the
page. This helps avoid a blocky appearance around letters and edges. The
filters are choices for the user: the best one depends on the document and
the quality of the original photograph.
""",
    ),
    (
        "How the Project Is Put Together",
        """
The interface is built with Streamlit, which lets the project run as a
local web application in a browser. OpenCV provides established image
operations such as edge detection and contour handling. NumPy supports the
project's image and coordinate calculations, including the custom
perspective-correction and image-warping steps.

The code is divided into small modules so that each part has a clear job.
One module looks for page corners, another calculates the perspective
mapping, another creates the warped image, and separate modules handle
filters and PDF creation. The main app connects these pieces to the
interactive screens.

This structure makes it easier to explain, test, and improve the system. It
also makes clear which operations are our own implementations and which use
widely used image-processing tools.
""",
    ),
    (
        "Testing the Scanner Fairly",
        """
One successful example is not enough to show that a document scanner is
useful. The project includes a set of twenty sample photographs with
different page angles, shadows, lighting conditions, backgrounds, and
visibility problems.

The benchmark view lets the group try the same application on these varied
examples and record which images were scanned correctly. Results should be
reported from an actual run of the app; the number of test images alone does
not prove that every scan succeeds.

The project also provides a comparison view for checking its custom warp
against OpenCV's established perspective-warping operation. Looking at the
result and the difference visualization can reveal mismatches that may not
be obvious from the original photo.
""",
    ),
    (
        "Demonstration for the Class",
        """
The live demonstration shows the complete user journey rather than only a
finished image. First, a classmate photographs a page or selects a prepared
sample. The group checks whether the page boundary was found correctly and
adjusts the corners if necessary.

Next, the scanner produces a straightened page. The presenter can compare
the original photograph with the corrected result, try a suitable cleanup
filter, and explain what changed. Finally, the class can see the available
download options for saving a clean image or document.

For a phone-based demonstration, the app must be running on a computer that
the phone can reach over the same local network. The group should prepare
the computer and connection before presenting, and should keep a sample
photograph ready in case the classroom network or camera is unavailable.
""",
    ),
    (
        "What Works Well and What Can Be Difficult",
        """
DocuScan brings several useful steps together in one place: it can locate a
page automatically, correct perspective, offer manual corner adjustment,
apply cleanup filters, and export a result. The sample collection and
comparison tools also give the group a practical way to explore its
behaviour.

The quality of the result still depends on the photograph. A page that is
partly outside the frame, covered by an object, badly blurred, or almost the
same colour as the table may be difficult to detect. Strong shadows and
curved paper can also reduce the quality of the final scan.

The scanner should therefore be presented as a helpful tool with a manual
fallback, not as a system that will always produce a perfect result. Showing
both its strengths and its difficult cases gives a more honest account of
the project.
""",
    ),
    (
        "Lessons Learned and Future Improvements",
        """
The project demonstrates that a useful graphics application is more than
one clever image transformation. It needs a complete path from input to
output, a way to recover when automatic detection is uncertain, clear user
controls, and a way to check results on more than one example.

There are several natural opportunities for future work. Detection could be
made more reliable on low-contrast or curved pages. The interface could
provide clearer guidance when corners are uncertain. The group could
evaluate quality using a larger collection of real photographs and record
the results consistently.

Other possible extensions include recognizing printed text, handling
multiple pages more efficiently, or adding more document formats. These are
future improvements rather than features that should be claimed as already
included in this version.
""",
    ),
    (
        "Conclusion",
        """
DocuScan helps turn an ordinary phone photograph into a more useful digital
document. It finds the page, corrects the view, offers cleanup choices, and
lets the user save the result. Its manual controls acknowledge that real
photographs are varied and that automatic image processing can make
mistakes.

The project brings together computer graphics concepts and practical
software design: the app has to interpret an image, transform it into a new
view, improve its presentation, and give the user a clear way to review the
outcome.

For the presentation, focus on the user problem, show the scanner working,
explain the steps in everyday language, and report only results observed
during testing. The key message is simple: DocuScan makes document
photographs easier to read, share, and store.
""",
    ),
]


def render_slides():
    st.markdown('<p class="main-header">🖥️ Presentation Slide Deck</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">English-first edition • CSSD 315 Computer Graphics • '
        'Brief 6: Document Scanner App</p>',
        unsafe_allow_html=True,
    )
    st.caption("Revised presentation — the previous technical-maths deck is superseded.")

    slide_index_key = "english_slide_idx"
    if slide_index_key not in st.session_state:
        st.session_state[slide_index_key] = 0

    def go_to_slide(delta):
        st.session_state[slide_index_key] = max(
            0, min(len(SLIDES) - 1, st.session_state[slide_index_key] + delta)
        )

    nav_previous, nav_select, nav_next = st.columns([1, 4, 1])
    with nav_previous:
        st.button(
            "⬅️ Previous",
            on_click=go_to_slide,
            args=(-1,),
            use_container_width=True,
            disabled=st.session_state[slide_index_key] == 0,
            key="english_slide_previous",
        )
    with nav_select:
        selected_slide = st.selectbox(
            "Jump to slide:",
            SLIDES,
            index=st.session_state[slide_index_key],
            label_visibility="collapsed",
            key="english_slide_select",
        )
        selected_index = SLIDES.index(selected_slide)
        if selected_index != st.session_state[slide_index_key]:
            st.session_state[slide_index_key] = selected_index
            st.rerun()
    with nav_next:
        st.button(
            "Next ➡️",
            on_click=go_to_slide,
            args=(1,),
            use_container_width=True,
            disabled=st.session_state[slide_index_key] == len(SLIDES) - 1,
            key="english_slide_next",
        )

    index = st.session_state[slide_index_key]
    st.progress((index + 1) / len(SLIDES), text=f"Slide {index + 1} of {len(SLIDES)}")
    st.markdown("---")
    title, content = _SLIDE_CONTENT[index]
    st.markdown(f"## {title}")
    st.markdown(content)
