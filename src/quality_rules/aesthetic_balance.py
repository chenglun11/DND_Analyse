from .base import BaseQualityRule
import numpy

class AestheticBalanceRule(BaseQualityRule):
    """
    Aesthetic balance assessment based on visual design principles and game design theory.
    
    Theoretical foundations:
    1. Gestalt Principles (Wertheimer, 1923) - Proximity, Similarity, Continuity
    2. Visual Hierarchy Theory (Arnheim, 1954) - Balance and visual weight
    3. Game Design Aesthetics (Schell, 2008) - Unity and variety in level design
    4. Spatial Cognition (Lynch, 1960) - Legibility and spatial organization
    """
    
    @property
    def name(self):
        return "aesthetic_balance"

    @property
    def description(self):
        return "Aesthetic balance assessment based on Gestalt principles, visual hierarchy, and spatial cognition theory"

    def evaluate(self, dungeon_data):
        levels = dungeon_data.get('levels', [])
        if not levels:
            return 0.0, {"reason": "No level data"}
        
        level = levels[0]
        rooms = level.get('rooms', [])
        game_elements = level.get('game_elements', [])
        
        if not rooms:
            return 0.0, {"reason": "No room data"}
        
        # Calculate room size distribution
        room_sizes = []
        room_positions = []
        
        for room in rooms:
            # Calculate room area (assuming rectangular rooms)
            width = room.get('width', 1)
            height = room.get('height', 1)
            area = width * height
            room_sizes.append(area)
            
            # Get room center position
            x = room.get('position', {}).get('x', 0)
            y = room.get('position', {}).get('y', 0)
            room_positions.append((x, y))
        
        # Calculate aesthetic metrics based on theoretical foundations
        size_variance = numpy.var(room_sizes) if len(room_sizes) > 1 else 0.0
        avg_size = numpy.mean(room_sizes) if room_sizes else 0.0
        
        # 1. Gestalt Principles Assessment
        proximity_score = self._calculate_proximity_score(room_positions)
        similarity_score = self._calculate_similarity_score(room_sizes)
        continuity_score = self._calculate_continuity_score(room_positions, rooms)
        
        # 2. Visual Hierarchy Assessment (Arnheim, 1954)
        visual_weight_score = self._calculate_visual_weight_balance(room_sizes, room_positions)
        focal_point_score = self._calculate_focal_point_quality(room_positions, game_elements)
        
        # 3. Spatial Cognition Assessment (Lynch, 1960)
        legibility_score = self._calculate_spatial_legibility(room_positions, rooms)
        organization_score = self._calculate_spatial_organization(room_positions)
        
        # 4. Unity and Variety Assessment (Schell, 2008)
        unity_score = self._calculate_unity_score(room_sizes, room_positions)
        variety_score = self._calculate_variety_score(room_sizes, game_elements)
        
        # Scoring strategy based on theoretical thresholds
        score = 1.0
        
        # Gestalt Principles (30% weight)
        gestalt_score = (proximity_score + similarity_score + continuity_score) / 3
        if gestalt_score < 0.4:  # Poor gestalt principles
            score -= 0.3
        elif gestalt_score < 0.7:  # Moderate gestalt principles
            score -= 0.15
        
        # Visual Hierarchy (25% weight)
        hierarchy_score = (visual_weight_score + focal_point_score) / 2
        if hierarchy_score < 0.4:  # Poor visual hierarchy
            score -= 0.25
        elif hierarchy_score < 0.7:  # Moderate visual hierarchy
            score -= 0.1
        
        # Spatial Cognition (25% weight)
        spatial_score = (legibility_score + organization_score) / 2
        if spatial_score < 0.4:  # Poor spatial cognition
            score -= 0.25
        elif spatial_score < 0.7:  # Moderate spatial cognition
            score -= 0.1
        
        # Unity and Variety (20% weight)
        design_score = (unity_score + variety_score) / 2
        if design_score < 0.4:  # Poor unity/variety balance
            score -= 0.2
        elif design_score < 0.7:  # Moderate unity/variety balance
            score -= 0.1
        
        # Bonus for excellent design (based on Arnheim's balance theory)
        if gestalt_score > 0.8 and hierarchy_score > 0.8:
            score += 0.1
        
        score = max(0.0, min(1.0, score))
        
        detail = {
            "room_count": len(rooms),
            "avg_room_size": avg_size,
            "size_variance": size_variance,
            "gestalt_score": gestalt_score,
            "proximity_score": proximity_score,
            "similarity_score": similarity_score,
            "continuity_score": continuity_score,
            "hierarchy_score": hierarchy_score,
            "visual_weight_score": visual_weight_score,
            "focal_point_score": focal_point_score,
            "spatial_score": spatial_score,
            "legibility_score": legibility_score,
            "organization_score": organization_score,
            "design_score": design_score,
            "unity_score": unity_score,
            "variety_score": variety_score,
            "theoretical_foundations": [
                "Gestalt Principles (Wertheimer, 1923)",
                "Visual Hierarchy Theory (Arnheim, 1954)", 
                "Game Design Aesthetics (Schell, 2008)",
                "Spatial Cognition (Lynch, 1960)"
            ]
        }
        
        return score, detail
    
    def _calculate_proximity_score(self, positions):
        """
        Gestalt Principle: Proximity - Elements close together are perceived as related
        Based on: Wertheimer, M. (1923). Laws of organization in perceptual forms.
        """
        if len(positions) < 2:
            return 1.0
        
        # Calculate average distance between all pairs
        distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = numpy.sqrt((positions[i][0] - positions[j][0])**2 + 
                                (positions[i][1] - positions[j][1])**2)
                distances.append(dist)
        
        avg_distance = numpy.mean(distances)
        distance_std = numpy.std(distances)
        
        # Optimal proximity: moderate clustering (not too close, not too far)
        # Based on empirical studies of visual grouping
        if avg_distance < 2.0:  # Too clustered
            return 0.3
        elif avg_distance < 5.0:  # Good proximity
            return 0.9
        elif avg_distance < 8.0:  # Moderate proximity
            return 0.6
        else:  # Too scattered
            return 0.2
    
    def _calculate_similarity_score(self, sizes):
        """
        Gestalt Principle: Similarity - Similar elements are perceived as related
        Based on: Wertheimer, M. (1923). Laws of organization in perceptual forms.
        """
        if len(sizes) < 2:
            return 1.0
        
        # Calculate coefficient of variation (CV = std/mean)
        cv = numpy.std(sizes) / numpy.mean(sizes) if numpy.mean(sizes) > 0 else 0
        
        # Optimal similarity: moderate variation (not too uniform, not too diverse)
        # Based on visual design research (Tractinsky et al., 2000)
        if cv < 0.1:  # Too uniform
            return 0.4
        elif cv < 0.3:  # Good similarity with variety
            return 0.9
        elif cv < 0.5:  # Moderate similarity
            return 0.7
        else:  # Too diverse
            return 0.3
    
    def _calculate_continuity_score(self, positions, rooms):
        """
        Gestalt Principle: Continuity - Elements arranged in smooth curves are perceived as related
        Based on: Wertheimer, M. (1923). Laws of organization in perceptual forms.
        """
        if len(positions) < 3:
            return 1.0
        
        # Calculate how well rooms form continuous paths
        # This is a simplified version - in practice would analyze actual connections
        center_x = numpy.mean([pos[0] for pos in positions])
        center_y = numpy.mean([pos[1] for pos in positions])
        
        # Calculate angular distribution around center
        angles = []
        for pos in positions:
            angle = numpy.arctan2(pos[1] - center_y, pos[0] - center_x)
            angles.append(angle)
        
        # Check for smooth angular distribution
        angles.sort()
        angle_gaps = []
        for i in range(len(angles) - 1):
            gap = angles[i + 1] - angles[i]
            angle_gaps.append(gap)
        
        avg_gap = numpy.mean(angle_gaps) if angle_gaps else 0
        gap_std = numpy.std(angle_gaps) if len(angle_gaps) > 1 else 0
        
        # Smooth distribution = low gap variance
        if gap_std < 0.5:  # Very smooth
            return 0.9
        elif gap_std < 1.0:  # Moderately smooth
            return 0.7
        else:  # Irregular
            return 0.4
    
    def _calculate_visual_weight_balance(self, sizes, positions):
        """
        Visual Hierarchy: Balance of visual weight
        Based on: Arnheim, R. (1954). Art and visual perception.
        """
        if len(sizes) < 2:
            return 1.0
        
        # Calculate center of visual mass
        total_weight = sum(sizes)
        weighted_x = sum(sizes[i] * positions[i][0] for i in range(len(sizes)))
        weighted_y = sum(sizes[i] * positions[i][1] for i in range(len(sizes)))
        
        center_x = weighted_x / total_weight if total_weight > 0 else 0
        center_y = weighted_y / total_weight if total_weight > 0 else 0
        
        # Calculate balance around center
        left_weight = sum(sizes[i] for i in range(len(sizes)) if positions[i][0] < center_x)
        right_weight = sum(sizes[i] for i in range(len(sizes)) if positions[i][0] > center_x)
        top_weight = sum(sizes[i] for i in range(len(sizes)) if positions[i][1] < center_y)
        bottom_weight = sum(sizes[i] for i in range(len(sizes)) if positions[i][1] > center_y)
        
        # Balance ratio (closer to 1.0 = more balanced)
        horizontal_balance = min(left_weight, right_weight) / max(left_weight, right_weight) if max(left_weight, right_weight) > 0 else 1.0
        vertical_balance = min(top_weight, bottom_weight) / max(top_weight, bottom_weight) if max(top_weight, bottom_weight) > 0 else 1.0
        
        return (horizontal_balance + vertical_balance) / 2
    
    def _calculate_focal_point_quality(self, positions, game_elements):
        """
        Visual Hierarchy: Quality of focal points
        Based on: Arnheim, R. (1954). Art and visual perception.
        """
        if not game_elements:
            return 0.5  # Neutral if no elements
        
        # Find important elements (bosses, special items)
        important_elements = [elem for elem in game_elements if elem.get('type') in ['boss', 'special']]
        
        if not important_elements:
            return 0.6  # No focal points
        
        # Check if important elements are well-positioned (not clustered)
        important_positions = [(elem.get('position', {}).get('x', 0), elem.get('position', {}).get('y', 0)) 
                              for elem in important_elements]
        
        if len(important_positions) < 2:
            return 0.8  # Single focal point is fine
        
        # Calculate spread of important elements
        center_x = numpy.mean([pos[0] for pos in important_positions])
        center_y = numpy.mean([pos[1] for pos in important_positions])
        
        distances = [numpy.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2) 
                    for pos in important_positions]
        
        avg_distance = numpy.mean(distances)
        
        # Good focal point distribution: moderate spread
        if avg_distance < 2.0:  # Too clustered
            return 0.3
        elif avg_distance < 6.0:  # Good spread
            return 0.9
        else:  # Too scattered
            return 0.6
    
    def _calculate_spatial_legibility(self, positions, rooms):
        """
        Spatial Cognition: Legibility of spatial layout
        Based on: Lynch, K. (1960). The image of the city.
        """
        if len(positions) < 2:
            return 1.0
        
        # Calculate spatial clarity (how easy it is to understand the layout)
        # This is a simplified version - would need actual connection data for full analysis
        
        # Check for clear spatial patterns
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        
        # Good legibility: clear spatial boundaries
        if x_range > 0 and y_range > 0:
            aspect_ratio = x_range / y_range
            if 0.5 < aspect_ratio < 2.0:  # Good proportions
                return 0.9
            elif 0.3 < aspect_ratio < 3.0:  # Acceptable proportions
                return 0.7
            else:  # Poor proportions
                return 0.4
        else:
            return 0.5
    
    def _calculate_spatial_organization(self, positions):
        """
        Spatial Cognition: Organization of spatial elements
        Based on: Lynch, K. (1960). The image of the city.
        """
        if len(positions) < 3:
            return 1.0
        
        # Calculate spatial organization using nearest neighbor analysis
        distances = []
        for i in range(len(positions)):
            min_dist = float('inf')
            for j in range(len(positions)):
                if i != j:
                    dist = numpy.sqrt((positions[i][0] - positions[j][0])**2 + 
                                    (positions[i][1] - positions[j][1])**2)
                    min_dist = min(min_dist, dist)
            distances.append(min_dist)
        
        avg_nearest_dist = numpy.mean(distances)
        dist_std = numpy.std(distances)
        
        # Good organization: consistent spacing
        if dist_std < avg_nearest_dist * 0.3:  # Very organized
            return 0.9
        elif dist_std < avg_nearest_dist * 0.6:  # Moderately organized
            return 0.7
        else:  # Poorly organized
            return 0.4
    
    def _calculate_unity_score(self, sizes, positions):
        """
        Unity: Coherence of the overall design
        Based on: Schell, J. (2008). The art of game design.
        """
        if len(sizes) < 2:
            return 1.0
        
        # Unity through consistent design elements
        size_cv = numpy.std(sizes) / numpy.mean(sizes) if numpy.mean(sizes) > 0 else 0
        
        # Calculate spatial unity (how well elements work together)
        center_x = numpy.mean([pos[0] for pos in positions])
        center_y = numpy.mean([pos[1] for pos in positions])
        
        distances_from_center = [numpy.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2) 
                                for pos in positions]
        distance_cv = numpy.std(distances_from_center) / numpy.mean(distances_from_center) if numpy.mean(distances_from_center) > 0 else 0
        
        # Unity score: balance of consistency and coherence
        size_unity = 1.0 - min(1.0, size_cv)
        spatial_unity = 1.0 - min(1.0, distance_cv)
        
        return (size_unity + spatial_unity) / 2
    
    def _calculate_variety_score(self, sizes, game_elements):
        """
        Variety: Diversity and interest in the design
        Based on: Schell, J. (2008). The art of game design.
        """
        if len(sizes) < 2:
            return 0.5
        
        # Variety through size differences
        size_cv = numpy.std(sizes) / numpy.mean(sizes) if numpy.mean(sizes) > 0 else 0
        
        # Variety through element types
        element_types = set(elem.get('type', 'unknown') for elem in game_elements)
        type_variety = min(1.0, len(element_types) / 5.0)  # Normalize to 0-1
        
        # Optimal variety: moderate size variation + good element diversity
        size_variety = min(1.0, size_cv * 2)  # Scale CV to 0-1
        
        return (size_variety + type_variety) / 2 