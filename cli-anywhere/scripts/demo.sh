#!/usr/bin/env bash
# Demo script for CLI-Anything showcase video
# Duration: ~90 seconds

set -e

echo "=== CLI-Anything Demo ==="
echo ""

# 1. Install
echo ">>> Step 1: Install (5s)"
echo "$ pip install cli-anything"
echo "$ cli-anything install gimp"
echo ""

# 2. GIMP - Image processing
echo ">>> Step 2: GIMP - Resize and convert (10s)"
echo "$ cli-anything-gimp batch resize input.jpg --width 800 --output resized.jpg"
echo ""

# 3. Blender - 3D
echo ">>> Step 3: Blender - Render scene (10s)"
echo "$ cli-anything-blender render scene.blend --output render.png --engine CYCLES"
echo ""

# 4. FreeCAD - CAD
echo ">>> Step 4: FreeCAD - Parametric modeling (15s)"
echo "$ cli-anything-freecad doc new --name Bracket"
echo "$ cli-anything-freecad shape box --length 40 --width 20 --height 5"
echo "$ cli-anything-freecad shape cylinder --radius 3 --height 6 --x 10 --y 10"
echo "$ cli-anything-freecad boolean cut Box Cylinder"
echo "$ cli-anything-freecad export to bracket.step"
echo ""

# 5. VLC - Media
echo ">>> Step 5: VLC - Transcode video (10s)"
echo "$ cli-anything-vlc transcode convert video.mp4 output.webm --profile webm-vp9-opus"
echo ""

# 6. AI Agent integration
echo ">>> Step 6: AI Agent (30s)"
echo "User: 'Create a thumbnail from this video at 1:30, resize to 320x180, and optimize it'"
echo ""
echo "Agent calls:"
echo "  1. cli-anything-vlc playback screenshot video.mp4 thumb.png --time 00:01:30"
echo "  2. cli-anything-imagemagick resize thumb.png thumb_320.png --width 320 --height 180"
echo "  3. cli-anything-imagemagick convert thumb_320.png thumb_opt.png --quality 85"
echo ""
echo "Agent: 'Done! Here's your optimized thumbnail.'"
echo ""

echo "=== End Demo ==="
