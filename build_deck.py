import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen Presentation (Streamlined 5-Slide 4-Minute Competition Deck)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# ZeroTouch Executive Brand Palette
C_BG = RGBColor(15, 15, 20)        # Midnight Ink #0F0F14
C_CARD = RGBColor(24, 24, 32)      # Hard Graphite #181820
C_GOLD = RGBColor(212, 175, 106)   # Champagne Gold #D4AF6A
C_GOLD_MUTED = RGBColor(181, 147, 80)
C_WHITE = RGBColor(242, 239, 233)  # Soft White #F2EFE9
C_GRAY = RGBColor(138, 141, 147)   # Cool Gray #8A8D93
C_ACCENT = RGBColor(74, 111, 165)  # Slate Blue #4A6FA5

def create_base_slide():
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()
    return slide

def add_header(slide, title_text, category_text="ZEROTOUCH OS • UAT HACKATHON"):
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = C_GOLD
    p_c.font.name = 'Segoe UI'

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(0.9))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE
    p_t.font.name = 'Georgia'

def add_card(slide, left, top, width, height, title, body_bullets, accent_color=C_GOLD):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD
    card.line.color.rgb = accent_color
    card.line.width = Pt(1)

    pad = Inches(0.28)
    tb = slide.shapes.add_textbox(left + pad, top + pad, width - (pad * 2), height - (pad * 2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_head = tf.paragraphs[0]
    p_head.text = title
    p_head.font.size = Pt(19)
    p_head.font.bold = True
    p_head.font.color.rgb = accent_color
    p_head.font.name = 'Segoe UI'

    for b in body_bullets:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(14)
        p.font.color.rgb = C_WHITE
        p.font.name = 'Segoe UI'
        p.space_before = Pt(8)

# ==========================================
# SLIDE 1: Title & Hook (0:00 - 0:30)
# ==========================================
s1 = create_base_slide()
if os.path.exists('zerotouch.png'):
    s1.shapes.add_picture('zerotouch.png', Inches(5.86), Inches(1.3), Inches(1.6), Inches(1.6))

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(3.2), Inches(11.33), Inches(3.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.alignment = PP_ALIGN.CENTER
p1.text = "ZeroTouch OS"
p1.font.size = Pt(54)
p1.font.bold = True
p1.font.color.rgb = C_GOLD
p1.font.name = 'Georgia'

p2 = tf1.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
p2.text = "THE INVISIBLE SPATIAL PERIPHERAL FOR WINDOWS"
p2.font.size = Pt(15)
p2.font.bold = True
p2.font.color.rgb = C_WHITE
p2.font.name = 'Consolas'
p2.space_before = Pt(10)

p3 = tf1.add_paragraph()
p3.alignment = PP_ALIGN.CENTER
p3.text = "Executive Computer Vision • 100% Local Inferencing • Zero False Positives"
p3.font.size = Pt(14)
p3.font.color.rgb = C_GRAY
p3.font.name = 'Segoe UI'
p3.space_before = Pt(6)

p4 = tf1.add_paragraph()
p4.alignment = PP_ALIGN.CENTER
p4.text = "UAT Hackathon 2026: See / Analyze / Build"
p4.font.size = Pt(13)
p4.font.color.rgb = C_GOLD_MUTED
p4.font.name = 'Segoe UI'
p4.space_before = Pt(28)

# ==========================================
# SLIDE 2: The Core Problem & Our Solution (0:30 - 1:15)
# ==========================================
s2 = create_base_slide()
add_header(s2, "The Spatial Dilemma: Why Computer Vision Peripherals Fail", "01 • PROBLEM & THESIS")
add_card(s2, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8), 
         "The Problem: Too Noisy to Leave On",
         ["Accidental Triggers: Scratching face, typing, or grabbing a cup fires unintended clicks and commands.",
          "Privacy Paranoia: Users fear cameras streaming frames across networks or logging to disk.",
          "Distance & Posture Limits: Stepping back to present slides breaks hand tracking or trips false look-aways.",
          "Hardware Lockouts: Most CV software monopolizes the webcam, preventing Zoom, Teams, or Meet from opening."],
         C_GOLD)

add_card(s2, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8),
         "The Solution: The Invisible Peripheral",
         ["100% Volatile RAM: Zero video frames saved or transmitted; all inference runs strictly in local memory.",
          "Multimodal Intent Filtering: Physical typing lockout, gaze tracking, and reach boundaries eliminate misfires.",
          "Stage Mode: Automatic distance adaptation keeps controls responsive at 6–10 feet.",
          "Native OS Camera Sharing: Windows Camera Frame Server sharing allows simultaneous Google Meet and CV usage."],
         C_WHITE)

# ==========================================
# SLIDE 3: Context-Aware Intelligence (1:15 - 2:15)
# ==========================================
s3 = create_base_slide()
add_header(s3, "Context-Aware Architecture: One Engine, Three Modes", "02 • SPATIAL WORKFLOW")
add_card(s3, Inches(0.8), Inches(1.9), Inches(3.7), Inches(4.8),
         "Presentation Mode",
         ["Targets: PowerPoint, Google Slides, Keynote, PDF.",
          "Back-of-Hand Swipe: Advance or return slides seamlessly across the room.",
          "Open Palm Hold (0.5s): Blank/resume screen ('B').",
          "Stage Optimization: Disengages desk gaze lockouts so presenters can look at audience or slides freely."],
         C_GOLD)

add_card(s3, Inches(4.8), Inches(1.9), Inches(3.7), Inches(4.8),
         "Video Meeting Mode",
         ["Targets: Google Meet, Zoom, MS Teams, Webex.",
          "Ghost-Mute (Shh): Index finger to mouth directly toggles hardware microphone mute via Windows Core Audio.",
          "Open Palm Hold: Instant camera toggle ('Alt + V').",
          "Back-of-Hand Swipe: Toggle participant views."],
         C_WHITE)

add_card(s3, Inches(8.8), Inches(1.9), Inches(3.7), Inches(4.8),
         "Media & Default Mode",
         ["Targets: Spotify, YouTube, Netflix, Desktop.",
          "Open Palm Hold: Smooth play/pause toggle.",
          "Dynamic Vertical Pinch: Continuous master volume control with live capsule HUD updates.",
          "Back-of-Hand Swipe: Skip or previous track."],
         C_ACCENT)

# ==========================================
# SLIDE 4: Multimodal Noise Rejection (2:15 - 3:00)
# ==========================================
s4 = create_base_slide()
add_header(s4, "Noise Defense: How We Eliminated False Triggers", "03 • COMPUTER VISION DEFENSE")
add_card(s4, Inches(0.8), Inches(1.9), Inches(5.6), Inches(2.3),
         "Smart Activity Lockout (Type & Click)",
         ["Background hardware hooks (Pynput) detect keyboard typing and mouse clicks.",
          "While typing or resting hands above the keyboard, gestures sleep for 1.8s."],
         C_GOLD)

add_card(s4, Inches(0.8), Inches(4.45), Inches(5.6), Inches(2.3),
         "Gaze-Clutch (Look-to-Control)",
         ["Real-time 3D head yaw and pupillary distance tracking.",
          "Glancing away at another screen automatically clutches gestures to standby."],
         C_WHITE)

add_card(s4, Inches(6.8), Inches(1.9), Inches(5.7), Inches(2.3),
         "ShoulderGuard Intruder Shield",
         ["Continuous BlazeFace scan monitors for shoulder surfers in public spaces.",
          "If a second face appears behind you, automatically fires Win+D to protect sensitive work."],
         C_ACCENT)

add_card(s4, Inches(6.8), Inches(4.45), Inches(5.7), Inches(2.3),
         "Body Ownership & Anti-Jitter Physics",
         ["Calculates Euclidean distance between wrist and face; rejects passerby hands.",
          "Bone length stability and acceleration checks freeze hallucinated hand joints."],
         C_GOLD)

# ==========================================
# SLIDE 5: Technical Architecture & Wrap-Up (3:00 - 4:00)
# ==========================================
s5 = create_base_slide()
add_header(s5, "Technical Architecture & Hackathon Wrap-Up", "04 • ARCHITECTURE & SUMMARY")
add_card(s5, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8),
         "High-Performance System Architecture",
         ["Shared Memory IPC: Zero-copy multiprocessing.shared_memory streams 30 FPS telemetry and previews to GUI.",
          "Hardware Audio Hook: Direct Windows Core Audio (Pycaw) input endpoint volume control.",
          "Windows Camera Frame Server: OpenCV MSMF backend hooks svchost.exe -k Camera for native multi-app streaming.",
          "Ambient HUD: CustomTkinter executive dashboard + topmost micro-pill Floating Capsule."],
         C_ACCENT)

add_card(s5, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8),
         "Summary & Why ZeroTouch Wins",
         ["Executive Polish: Enterprise-ready companion built for everyday work, not a tech demo.",
          "Zero Cloud Risk: True local privacy that enterprise users can actually deploy.",
          "Production Ready: Complete with 1-click batch launcher, custom Windows taskbar branding, and system tray integration.",
          "Open Source: https://github.com/Philphil-org/UAT-Hackathon"],
         C_GOLD)

output_path = 'ZeroTouch_PitchDeck.pptx'
prs.save(output_path)
print(f'Successfully generated clean 5-slide deck: {output_path}')

# Also try to overwrite ZeroTouch_Presentation.pptx if unlocked
try:
    prs.save('ZeroTouch_Presentation.pptx')
    print('Also updated ZeroTouch_Presentation.pptx')
except Exception as e:
    print('ZeroTouch_Presentation.pptx currently locked in PowerPoint (ZeroTouch_PitchDeck.pptx ready)')
