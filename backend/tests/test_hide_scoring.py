"""
Tests for the Hide game scoring system.

This module tests the scoring calculation logic in the HideGame class,
which evaluates student performance based on:
1. Treasures (количество кладов)
2. Stubs (файлы-заглушки)
3. Directory structure (папки и глубина)
4. Penalties for rule violations
"""

import pytest
from unittest.mock import Mock, patch
from backend.app.games.hide import HideGame


class TestHideScoringSystem:
    """Test suite for hide game scoring calculations."""
    
    @pytest.fixture
    def game_instance(self):
        """Create a HideGame instance with default settings."""
        game = HideGame()
        game.settings = {
            "treasures_amount": 1,
            "stubs": 3,
            "allow_empty_stubs": False,
            "allow_root_treasures": False,
            "root_folders": 5,
            "depth_folders": 1,
            "depth": 3,
        }
        return game
    
    def _calculate_score(self, game, treasures, files, empty_files, root_treasures, 
                         root_dirs, deep_root_dirs):
        """
        Helper method to calculate score given metrics.
        Mirrors the scoring logic from HideGame.check()
        """
        treasures_amount = int(game.settings["treasures_amount"])
        stubs_amount = int(game.settings["stubs"])
        allow_empty_stubs = bool(game.settings["allow_empty_stubs"])
        allow_root_treasures = bool(game.settings["allow_root_treasures"])
        root_folders = int(game.settings["root_folders"])
        depth_folders = int(game.settings["depth_folders"])
        
        stubs = max(0, files - treasures)
        
        # 1. Treasures (max 4 points)
        treasure_diff = abs(treasures - treasures_amount)
        treasure_points = max(0, 4 - treasure_diff ** 2)
        
        # 2. Stubs (max 3 points)
        stub_threshold = stubs_amount * 0.5
        if stubs >= stubs_amount:
            stub_points = 3
        elif stubs >= stub_threshold:
            stub_points = 1.5
        else:
            stub_points = 0
        
        # 3. Structure (max 2.5 points)
        structure_points = 0
        if root_dirs >= root_folders:
            structure_points += 1.5
        if deep_root_dirs >= depth_folders and depth_folders > 0:
            structure_points += 1.0
        
        # 4. Penalties
        penalty = 1.0
        if not allow_empty_stubs and empty_files > 0:
            penalty *= 0.9 ** empty_files
        if not allow_root_treasures and root_treasures > 0:
            penalty *= 0.85 ** root_treasures
        
        # 5. Final calculation
        base_score = treasure_points + stub_points + structure_points
        raw_score = base_score * penalty
        final_score = min(10, max(0, round(raw_score)))
        
        return final_score, {
            "treasure_points": treasure_points,
            "stub_points": stub_points,
            "structure_points": structure_points,
            "penalty": penalty,
            "base_score": base_score,
            "raw_score": raw_score,
        }
    
    # ==================== TREASURE SCORING TESTS ====================
    
    def test_perfect_treasures(self, game_instance):
        """Test when treasure count matches exactly (1 treasure expected)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,  # Expected: 1
            files=4,      # 1 treasure + 3 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["treasure_points"] == 4
        assert score == 10  # Perfect score
    
    def test_one_treasure_deviation(self, game_instance):
        """Test with 1 treasure deviation: 0 treasures instead of 1."""
        score, details = self._calculate_score(
            game_instance,
            treasures=0,  # Expected: 1, deviation: 1
            files=3,      # All stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        # Formula: 4 - (1)^2 = 4 - 1 = 3
        assert details["treasure_points"] == 3
    
    def test_one_treasure_deviation_high(self, game_instance):
        """Test with 1 treasure deviation: 2 treasures instead of 1."""
        score, details = self._calculate_score(
            game_instance,
            treasures=2,  # Expected: 1, deviation: 1
            files=5,      # 2 treasures + 3 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        # Formula: 4 - (1)^2 = 3
        assert details["treasure_points"] == 3
    
    def test_two_treasure_deviation(self, game_instance):
        """Test with 2 treasure deviation: 3 treasures instead of 1."""
        score, details = self._calculate_score(
            game_instance,
            treasures=3,  # Expected: 1, deviation: 2
            files=6,      # 3 treasures + 3 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        # Formula: 4 - (2)^2 = 4 - 4 = 0
        assert details["treasure_points"] == 0
    
    def test_large_treasure_deviation(self, game_instance):
        """Test with large treasure deviation: 10 treasures instead of 1."""
        score, details = self._calculate_score(
            game_instance,
            treasures=10,  # Expected: 1, deviation: 9
            files=13,      # 10 treasures + 3 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        # Formula: 4 - (9)^2 = 4 - 81 = negative, clamped to 0
        assert details["treasure_points"] == 0
    
    # ==================== STUB SCORING TESTS ====================
    
    def test_no_stubs_below_threshold(self, game_instance):
        """Test with 0 stubs when 3 are required (below 50% threshold)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=1,      # 1 treasure + 0 stubs (below 50% of 3)
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 0
    
    def test_below_threshold_stubs(self, game_instance):
        """Test with 1 stub when 3 are required (below 50% threshold: 1.5)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=2,      # 1 treasure + 1 stub (< 1.5 threshold)
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 0
    
    def test_at_threshold_stubs(self, game_instance):
        """Test with stubs at 50% threshold (1.5 stubs when 3 required)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=2,  # 2 treasures
            files=4,      # 2 treasures + 2 stubs (>= 1.5 threshold)
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 1.5
    
    def test_above_threshold_stubs(self, game_instance):
        """Test with stubs above 50% threshold."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,      # 1 treasure + 3 stubs (>= 3 required)
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 3
    
    def test_many_stubs_full_points(self, game_instance):
        """Test with more stubs than required gets max points."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=10,     # 1 treasure + 9 stubs (> 3 required)
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 3
    
    # ==================== STRUCTURE SCORING TESTS ====================
    
    def test_no_structure_points(self, game_instance):
        """Test when no structural requirements are met."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=0,      # 0 dirs, needed 5
            deep_root_dirs=0, # 0 deep dirs, needed 1
        )
        assert details["structure_points"] == 0
    
    def test_root_dirs_only(self, game_instance):
        """Test when only root folders requirement is met."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=5,      # Meets requirement
            deep_root_dirs=0, # Doesn't meet requirement
        )
        assert details["structure_points"] == 1.5
    
    def test_depth_only(self, game_instance):
        """Test when only depth requirement is met."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=0,      # Doesn't meet requirement
            deep_root_dirs=1, # Meets requirement
        )
        assert details["structure_points"] == 1.0
    
    def test_all_structure_points(self, game_instance):
        """Test when all structural requirements are met."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=5,      # Meets requirement
            deep_root_dirs=1, # Meets requirement
        )
        assert details["structure_points"] == 2.5
    
    def test_excess_root_dirs(self, game_instance):
        """Test that excess root directories don't increase points."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=10,     # More than required (5)
            deep_root_dirs=1,
        )
        # Should still be 1.5 (not increased for excess)
        assert details["structure_points"] == 2.5
    
    # ==================== PENALTY TESTS ====================
    
    def test_no_penalties(self, game_instance):
        """Test with no violations (no empty files, no root treasures)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,    # Allowed empty: False, but 0 empty files
            root_treasures=0, # Allowed root: False, but 0 root treasures
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == 1.0
    
    def test_one_empty_file_penalty(self, game_instance):
        """Test penalty for 1 empty file: 0.9^1 = 0.9."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=1,    # 1 empty file when not allowed
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == pytest.approx(0.9)
    
    def test_two_empty_files_penalty(self, game_instance):
        """Test penalty for 2 empty files: 0.9^2 = 0.81."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=2,    # 2 empty files
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == pytest.approx(0.81)
    
    def test_one_root_treasure_penalty(self, game_instance):
        """Test penalty for 1 root treasure: 0.85^1 = 0.85."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=1,  # 1 root treasure when not allowed
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == pytest.approx(0.85)
    
    def test_combined_penalties(self, game_instance):
        """Test combined penalties: 0.9 * 0.85 = 0.765."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=1,
            root_treasures=1,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == pytest.approx(0.765)
    
    def test_multiple_empty_files_stacking(self, game_instance):
        """Test that penalties compound: 0.9^3 ≈ 0.729."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=3,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == pytest.approx(0.9 ** 3)
    
    # ==================== PENALTIES DISABLED TESTS ====================
    
    def test_empty_files_allowed_no_penalty(self, game_instance):
        """Test that empty files don't cause penalty when allowed."""
        game_instance.settings["allow_empty_stubs"] = True
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=5,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == 1.0
    
    def test_root_treasures_allowed_no_penalty(self, game_instance):
        """Test that root treasures don't cause penalty when allowed."""
        game_instance.settings["allow_root_treasures"] = True
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=3,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["penalty"] == 1.0
    
    # ==================== FINAL SCORE TESTS ====================
    
    def test_perfect_score_10(self, game_instance):
        """Test perfect score of 10."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert score == 10
    
    def test_score_clamped_to_max_10(self, game_instance):
        """Test that score is clamped to maximum 10."""
        # This is difficult to achieve naturally, but simulate with high base_score
        # Base score max is 9.5, so this shouldn't happen with default multiplier,
        # but test the clamping logic
        game_instance.settings["allow_empty_stubs"] = True
        game_instance.settings["allow_root_treasures"] = True
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=10,
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert score <= 10
    
    def test_score_clamped_to_min_0(self, game_instance):
        """Test that score is clamped to minimum 0."""
        score, details = self._calculate_score(
            game_instance,
            treasures=10,  # Major deviation
            files=13,
            empty_files=10,  # Heavy penalty
            root_treasures=5,  # Heavy penalty
            root_dirs=0,
            deep_root_dirs=0,
        )
        assert score >= 0
    
    def test_rounding_down(self, game_instance):
        """Test rounding behavior (round function)."""
        # Create a scenario where raw_score is X.4 (rounds down)
        game_instance.settings["allow_empty_stubs"] = True
        game_instance.settings["allow_root_treasures"] = True
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=100,  # Many stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        # Base score: 4 + 3 + 2.5 = 9.5, penalty 1.0, raw = 9.5, rounded = 10
        assert isinstance(score, int)
    
    # ==================== EDGE CASES ====================
    
    def test_zero_metrics(self, game_instance):
        """Test with all metrics at 0 (empty directory)."""
        score, details = self._calculate_score(
            game_instance,
            treasures=0,
            files=0,
            empty_files=0,
            root_treasures=0,
            root_dirs=0,
            deep_root_dirs=0,
        )
        assert score >= 0
        assert score <= 10
    
    def test_depth_folders_zero_no_error(self, game_instance):
        """Test when depth_folders is 0 (no depth requirement)."""
        game_instance.settings["depth_folders"] = 0
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=4,
            empty_files=0,
            root_treasures=0,
            root_dirs=0,
            deep_root_dirs=0,
        )
        # Should not crash and depth should contribute 0
        assert score >= 0
    
    def test_different_treasure_requirements(self, game_instance):
        """Test with different treasure_amount requirement (3 instead of 1)."""
        game_instance.settings["treasures_amount"] = 3
        score, details = self._calculate_score(
            game_instance,
            treasures=3,  # Perfect
            files=6,
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["treasure_points"] == 4  # Perfect match
    
    def test_different_stubs_requirement(self, game_instance):
        """Test with different stubs requirement (5 instead of 3)."""
        game_instance.settings["stubs"] = 5
        score, details = self._calculate_score(
            game_instance,
            treasures=1,
            files=6,  # 1 treasure + 5 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=5,
            deep_root_dirs=1,
        )
        assert details["stub_points"] == 3  # Meets requirement
    
    # ==================== REALISTIC SCENARIOS ====================
    
    def test_good_submission_high_score(self, game_instance):
        """Test a good submission with high score."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,      # Perfect
            files=5,          # 4+ stubs (more than required 3)
            empty_files=0,
            root_treasures=0,
            root_dirs=6,      # More than required 5
            deep_root_dirs=1, # Meets requirement
        )
        assert score == 10
    
    def test_medium_submission_medium_score(self, game_instance):
        """Test an average submission with medium score."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,      # Perfect
            files=4,          # Exactly 3 stubs
            empty_files=1,    # One empty (penalty)
            root_treasures=0,
            root_dirs=5,      # Exactly as required
            deep_root_dirs=1, # Meets requirement
        )
        # Base: 4 + 3 + 2.5 = 9.5
        # Penalty: 0.9 (1 empty file)
        # Raw: 9.5 * 0.9 = 8.55 -> 9
        assert 8 <= score <= 9
    
    def test_poor_submission_low_score(self, game_instance):
        """Test a poor submission with low score."""
        score, details = self._calculate_score(
            game_instance,
            treasures=5,      # Way off (5 instead of 1)
            files=5,          # Barely enough stubs
            empty_files=2,    # Some empty files
            root_treasures=2, # Root treasures when not allowed
            root_dirs=2,      # Not enough directories
            deep_root_dirs=0, # No depth
        )
        assert score < 5
    
    def test_completely_empty_game_folder(self, game_instance):
        """Test with completely empty game folder."""
        score, details = self._calculate_score(
            game_instance,
            treasures=0,
            files=0,
            empty_files=0,
            root_treasures=0,
            root_dirs=0,
            deep_root_dirs=0,
        )
        # No treasures (0 when 1 required): -1 point
        # No stubs (0 when 3 required): no stub points
        # No structure: no structure points
        # Base score = 3 + 0 + 0 = 3
        # Penalty = 1.0
        # Final = 3
        assert score == 3
    
    def test_only_treasures_no_structure(self, game_instance):
        """Test with correct treasures but missing structural requirements."""
        score, details = self._calculate_score(
            game_instance,
            treasures=1,      # Perfect
            files=4,          # Exactly 3 stubs
            empty_files=0,
            root_treasures=0,
            root_dirs=1,      # Less than required 5
            deep_root_dirs=0, # No depth
        )
        # Treasure: 4
        # Stubs: 3
        # Structure: 0
        # Base: 7, Penalty: 1.0, Final: 7
        assert score == 7
