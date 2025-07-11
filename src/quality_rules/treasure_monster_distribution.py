from .base import BaseQualityRule
import numpy

class TreasureMonsterDistributionRule(BaseQualityRule):
    @property
    def name(self):
        return "treasure_monster_distribution"

    @property
    def description(self):
        return "Treasure and monster distribution quality assessment, focusing on treasure density, monster density, boss distribution, value gradient, difficulty gradient, etc."

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        
        level = levels[0]
        rooms = level.get('rooms', [])
        game_elements = level.get('game_elements', [])
        
        if not rooms:
            return 0.0, {"reason": "No room data"}
        
        # Extract game elements by type
        treasures = []
        monsters = []
        bosses = []
        specials = []
        
        for element in game_elements:
            elem_type = element.get('type', '')
            if elem_type == 'treasure':
                treasures.append(element)
            elif elem_type == 'monster':
                monsters.append(element)
            elif elem_type == 'boss':
                bosses.append(element)
            elif elem_type == 'special':
                specials.append(element)
        
        room_count = len(rooms)
        treasure_density = len(treasures) / room_count if room_count else 0
        monster_density = len(monsters) / room_count if room_count else 0
        boss_count = len(bosses)
        special_count = len(specials)
        
        # Calculate spatial distribution metrics
        treasure_positions = [(t.get('position', {}).get('x', 0), t.get('position', {}).get('y', 0)) for t in treasures]
        monster_positions = [(m.get('position', {}).get('x', 0), m.get('position', {}).get('y', 0)) for m in monsters]
        
        # Calculate spatial spread (standard deviation of positions)
        treasure_spread = self._calculate_spatial_spread(treasure_positions)
        monster_spread = self._calculate_spatial_spread(monster_positions)
        
        # Calculate distance-based metrics
        treasure_monster_distance = self._calculate_avg_distance(treasure_positions, monster_positions)
        treasure_treasure_distance = self._calculate_avg_distance(treasure_positions, treasure_positions)
        monster_monster_distance = self._calculate_avg_distance(monster_positions, monster_positions)
        
        # Scoring strategy: balanced distribution with good spacing
        score = 1.0
        
        # Density checks
        if treasure_density < 0.1 or treasure_density > 0.6:
            score -= 0.2
        if monster_density < 0.1 or monster_density > 0.6:
            score -= 0.2
        
        # Boss presence
        if boss_count == 0:
            score -= 0.15
        elif boss_count > 3:
            score -= 0.1
        
        # Spatial distribution
        if treasure_spread < 2.0:  # Too clustered
            score -= 0.15
        if monster_spread < 2.0:  # Too clustered
            score -= 0.15
        
        # Distance checks
        if treasure_monster_distance < 3.0:  # Too close
            score -= 0.1
        if treasure_treasure_distance < 2.0:  # Too clustered
            score -= 0.1
        if monster_monster_distance < 2.0:  # Too clustered
            score -= 0.1
        
        # Special elements bonus
        if special_count > 0:
            score += 0.05  # Bonus for having special elements
        
        score = max(0.0, min(1.0, score))
        
        detail = {
            "treasure_density": treasure_density,
            "monster_density": monster_density,
            "boss_count": boss_count,
            "special_count": special_count,
            "treasure_spread": treasure_spread,
            "monster_spread": monster_spread,
            "treasure_monster_distance": treasure_monster_distance,
            "treasure_treasure_distance": treasure_treasure_distance,
            "monster_monster_distance": monster_monster_distance,
            "treasure_count": len(treasures),
            "monster_count": len(monsters),
            "room_count": room_count,
            "total_game_elements": len(game_elements)
        }
        
        return score, detail
    
    def _calculate_spatial_spread(self, positions):
        """Calculate spatial spread using standard deviation of positions"""
        if len(positions) < 2:
            return 0.0
        
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        x_std = numpy.std(x_coords) if len(x_coords) > 1 else 0.0
        y_std = numpy.std(y_coords) if len(y_coords) > 1 else 0.0
        
        return numpy.sqrt(x_std**2 + y_std**2)
    
    def _calculate_avg_distance(self, positions1, positions2):
        """Calculate average distance between two sets of positions"""
        if not positions1 or not positions2:
            return 0.0
        
        total_distance = 0.0
        count = 0
        
        for pos1 in positions1:
            for pos2 in positions2:
                if pos1 != pos2:  # Don't calculate distance to self
                    distance = numpy.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    total_distance += distance
                    count += 1
        
        return total_distance / count if count > 0 else 0.0 