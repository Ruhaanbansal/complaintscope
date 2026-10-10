"""
ComplaintScope: Master Pipeline Runner.
Executes all phases sequentially (Phase 2 through Phase 9).
Run: python -m src.pipeline [--phase N]
"""
import sys
import logging
import argparse
import time
from pathlib import Path

from src.config import setup_logger, load_config, set_seeds, save_run_metadata

logger = setup_logger("complaintscope.pipeline")


def run_all(start_phase: int = 2, end_phase: int = 9):
    """Run all phases from start_phase to end_phase inclusive."""
    cfg = load_config()
    set_seeds(cfg.get("seed", 42))
    overall_t0 = time.time()
    logger.info(f"=== ComplaintScope Pipeline: Phases {start_phase}–{end_phase} ===")

    phase_timings = {}

    if start_phase <= 2:
        logger.info("\n" + "="*60 + "\nPHASE 2: Preprocessing & Ablation\n" + "="*60)
        from src.preprocess import run_phase_2
        t0 = time.time()
        run_phase_2()
        phase_timings["Phase 2"] = round(time.time() - t0, 1)

    if start_phase <= 3:
        logger.info("\n" + "="*60 + "\nPHASE 3: Feature Representation\n" + "="*60)
        from src.features import run_phase_3
        t0 = time.time()
        run_phase_3()
        phase_timings["Phase 3"] = round(time.time() - t0, 1)

    if start_phase <= 4:
        logger.info("\n" + "="*60 + "\nPHASE 4: Product Classification\n" + "="*60)
        from src.classify import run_phase_4
        t0 = time.time()
        run_phase_4()
        phase_timings["Phase 4"] = round(time.time() - t0, 1)

    if start_phase <= 5:
        logger.info("\n" + "="*60 + "\nPHASE 5: Relief-Risk Prediction\n" + "="*60)
        from src.relief import run_phase_5
        t0 = time.time()
        run_phase_5()
        phase_timings["Phase 5"] = round(time.time() - t0, 1)

    if start_phase <= 6:
        logger.info("\n" + "="*60 + "\nPHASE 6: Topic Discovery\n" + "="*60)
        from src.topics import run_phase_6
        t0 = time.time()
        run_phase_6()
        phase_timings["Phase 6"] = round(time.time() - t0, 1)

    if start_phase <= 7:
        logger.info("\n" + "="*60 + "\nPHASE 7: Emerging-Issue Detection\n" + "="*60)
        from src.burst import run_phase_7
        t0 = time.time()
        run_phase_7()
        phase_timings["Phase 7"] = round(time.time() - t0, 1)

    if start_phase <= 8:
        logger.info("\n" + "="*60 + "\nPHASE 8: Network Analysis\n" + "="*60)
        from src.network import run_phase_8
        t0 = time.time()
        run_phase_8()
        phase_timings["Phase 8"] = round(time.time() - t0, 1)

    if start_phase <= 9:
        logger.info("\n" + "="*60 + "\nPHASE 9: Systemic Risk Index\n" + "="*60)
        from src.sri import run_phase_9
        t0 = time.time()
        run_phase_9()
        phase_timings["Phase 9"] = round(time.time() - t0, 1)

    total = round(time.time() - overall_t0, 1)
    logger.info(f"\n{'='*60}")
    logger.info(f"Pipeline complete in {total:.1f}s")
    for ph, t in phase_timings.items():
        logger.info(f"  {ph}: {t:.1f}s")
    logger.info('='*60)
    return phase_timings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComplaintScope Pipeline Runner")
    parser.add_argument("--start", type=int, default=2, help="Start phase (default: 2)")
    parser.add_argument("--end",   type=int, default=9, help="End phase (default: 9)")
    args = parser.parse_args()
    run_all(start_phase=args.start, end_phase=args.end)
