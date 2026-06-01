# Convert images to pdf
#
# Dual-mode tool: run with image paths for CLI, or with no arguments for GUI.
#
# Based on:
# - https://datatofish.com/images-to-pdf-python/#:~:text=%20Steps%20to%20Convert%20Images%20to%20PDF%20using,the%20image%20to%20PDF%20using%20Python%20More%20
# - https://stackoverflow.com/questions/48278187/argparse-what-is-the-difference-between-sys-argv1-and-args-input
#
# CLI examples:
#   python convert_images_to_pdf.py data/image_1.jpeg data/image_2.jpeg data/image_3.jpeg
#   python convert_images_to_pdf.py -o myfile.pdf img1.jpg img2.png

from __future__ import annotations

import argparse
import ctypes
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Sequence

from PIL import Image, UnidentifiedImageError


def convert_images_to_pdf(
    image_paths: Sequence[str | Path],
    output_path: str | Path = "merge.pdf",
) -> None:
    """Convert an ordered list of images into a single multi-page PDF.

    Args:
        image_paths: Paths to image files (order is preserved in the PDF).
        output_path: Destination PDF file path (default: merge.pdf in current directory).

    Raises:
        ValueError: If no images are provided.
        FileNotFoundError: If any input image does not exist.
        UnidentifiedImageError: If any input is not a valid image.
        OSError: For permission or I/O errors when reading/writing files.
    """
    if not image_paths:
        raise ValueError("At least one image path is required")

    paths = [Path(p) for p in image_paths]
    output = Path(output_path)

    pil_images: list[Image.Image] = []
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {p}")
        try:
            pil_images.append(Image.open(p))
        except UnidentifiedImageError:
            raise UnidentifiedImageError(f"Not a supported image file: {p}") from None

    # Convert all pages to RGB (required for PDF)
    rgb_images = [img.convert("RGB") for img in pil_images]

    # First image is the base; remaining images are appended
    first, *rest = rgb_images
    first.save(output, save_all=True, append_images=rest)


def cli_main(argv: Sequence[str] | None = None) -> None:
    """Command-line interface entry point using argparse."""
    parser = argparse.ArgumentParser(
        prog="convert_images_to_pdf",
        description="Convert an ordered list of images into a single PDF file.",
    )
    parser.add_argument(
        "images",
        nargs="+",
        help="One or more image files in the desired PDF page order.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="merge.pdf",
        help="Output PDF filename (default: merge.pdf)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.2.0 (Tkinter GUI edition)",
    )

    args = parser.parse_args(argv)

    try:
        convert_images_to_pdf(args.images, args.output)
        out_path = Path(args.output).resolve()
        print(f"Created: {out_path}")
    except Exception as e:
        parser.error(f"{type(e).__name__}: {e}")


def _hide_console_on_windows() -> None:
    """Best-effort hide of the console window when launched as GUI on Windows.

    This gives a clean double-click experience for the GUI while preserving
    full console output/behavior when the exe is invoked with arguments (CLI mode).
    A brief flash can still occur because the subsystem is chosen at build time.
    """
    if sys.platform != "win32":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except Exception:
        # Best effort only — never break the app because of this
        pass


def gui_main() -> None:
    """Launch the Tkinter GUI for selecting images, reordering, and converting to PDF."""
    _hide_console_on_windows()

    root = tk.Tk()
    root.title("Images → PDF")
    root.geometry("720x520")
    root.minsize(600, 420)

    # Internal list of full paths (order matters)
    selected_paths: list[Path] = []

    def refresh_listbox() -> None:
        listbox.delete(0, tk.END)
        for p in selected_paths:
            listbox.insert(tk.END, p.name)  # show basename for readability
        convert_btn.config(state="normal" if selected_paths else "disabled")

    def add_images() -> None:
        files = filedialog.askopenfilenames(
            title="Select images (in desired order)",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif"),
                ("All files", "*.*"),
            ],
        )
        if not files:
            return
        for f in files:
            p = Path(f)
            if p not in selected_paths:
                selected_paths.append(p)
        refresh_listbox()

    def remove_selected() -> None:
        sel = list(listbox.curselection())
        if not sel:
            return
        # Remove from the end to preserve indices
        for index in reversed(sel):
            del selected_paths[index]
        refresh_listbox()

    def move_up() -> None:
        sel = list(listbox.curselection())
        if not sel or sel[0] == 0:
            return
        for index in sel:
            selected_paths[index - 1], selected_paths[index] = (
                selected_paths[index],
                selected_paths[index - 1],
            )
        refresh_listbox()
        # Re-select the moved items
        for index in sel:
            listbox.selection_set(index - 1)

    def move_down() -> None:
        sel = list(listbox.curselection())
        if not sel or sel[-1] == len(selected_paths) - 1:
            return
        for index in reversed(sel):
            selected_paths[index + 1], selected_paths[index] = (
                selected_paths[index],
                selected_paths[index + 1],
            )
        refresh_listbox()
        for index in sel:
            listbox.selection_set(index + 1)

    def clear_all() -> None:
        selected_paths.clear()
        refresh_listbox()

    def browse_output() -> None:
        initial = output_var.get() or "merge.pdf"
        filename = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            initialfile=initial,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if filename:
            output_var.set(filename)

    def do_convert() -> None:
        if not selected_paths:
            messagebox.showwarning("No images", "Please add at least one image.")
            return

        output = output_var.get().strip() or "merge.pdf"
        try:
            convert_images_to_pdf(selected_paths, output)
            out_path = Path(output).resolve()
            messagebox.showinfo(
                "Success",
                f"PDF created successfully:\n{out_path}",
            )
            # Offer to open the PDF on Windows (nice UX, zero extra deps)
            if sys.platform == "win32" and messagebox.askyesno(
                "Open PDF?", "Would you like to open the created PDF now?"
            ):
                try:
                    os.startfile(str(out_path))
                except Exception:
                    pass  # best effort
            # Optionally clear the list after successful conversion
            # selected_paths.clear()
            # refresh_listbox()
        except Exception as e:
            messagebox.showerror("Conversion failed", f"{type(e).__name__}: {e}")

    # === Layout ===
    main_frame = ttk.Frame(root, padding=12)
    main_frame.pack(fill="both", expand=True)

    # Title
    ttk.Label(main_frame, text="Convert Images to PDF", font=("Segoe UI", 14, "bold")).pack(
        anchor="w", pady=(0, 8)
    )

    # List + controls
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill="both", expand=True, pady=(0, 8))

    listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=12)
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    # Button column
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill="x", pady=(0, 8))

    ttk.Button(btn_frame, text="Add Images...", command=add_images).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Remove", command=remove_selected).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Move ↑", command=move_up).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Move ↓", command=move_down).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Clear", command=clear_all).pack(side="left", padx=2)

    # Output path
    out_frame = ttk.Frame(main_frame)
    out_frame.pack(fill="x", pady=(0, 8))

    ttk.Label(out_frame, text="Output PDF:").pack(side="left")
    output_var = tk.StringVar(value="merge.pdf")
    out_entry = ttk.Entry(out_frame, textvariable=output_var, width=50)
    out_entry.pack(side="left", fill="x", expand=True, padx=4)
    ttk.Button(out_frame, text="Browse...", command=browse_output).pack(side="left")

    # Convert button
    convert_btn = ttk.Button(
        main_frame, text="Convert to PDF", command=do_convert, state="disabled"
    )
    convert_btn.pack(fill="x", pady=6)

    # Status / help
    help_text = (
        "Tip: Add images in the order you want them to appear in the PDF. "
        "Use Move ↑/↓ to reorder. The same .exe works from the command line too."
    )
    ttk.Label(main_frame, text=help_text, foreground="#666", wraplength=680).pack(
        anchor="w", pady=(4, 0)
    )

    # Keyboard shortcuts
    root.bind("<Delete>", lambda e: remove_selected())
    root.bind("<Control-q>", lambda e: root.destroy())

    root.mainloop()


if __name__ == "__main__":
    # Dual-mode hybrid:
    #   - Any arguments (images or flags) → CLI via argparse
    #   - No arguments → launch Tkinter GUI (with Windows console hiding)
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()
else:
    pass
