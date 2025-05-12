// FilterBar.tsx
import React from 'react';
import { ScrollView, Text, View, StyleSheet, TouchableOpacity } from 'react-native';

const FILTERS = [
  'Night Club',
  'Cocktail Bar',
  'Sports Bar',
  'Karaoke',
  'Lounge',
  'Live Music',
  'Dive Bar',
  'LGBTQ+ Friendly'
];

interface FilterBarProps {
  selected: string | null;
  onSelect: (value: string | null) => void;
}

export default function FilterBar({ selected, onSelect }: FilterBarProps) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.container}>
      {FILTERS.map((label) => {
        const isSelected = selected === label;
        return (
          <TouchableOpacity
            key={label}
            onPress={() => onSelect(isSelected ? null : label)}
            style={[styles.chip, isSelected && styles.selectedChip]}
          >
            <Text style={[styles.chipText, isSelected && styles.selectedText]}>
              {label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 8,
    marginBottom: 12,
    flexGrow: 0,
  },
  chip: {
    backgroundColor: '#222',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    marginRight: 8,
  },
  chipText: {
    color: '#9FDDE1',
    fontSize: 14,
  },
  selectedChip: {
    backgroundColor: '#9FDDE1',
  },
  selectedText: {
    color: '#000',
    fontWeight: '600',
  },
});
