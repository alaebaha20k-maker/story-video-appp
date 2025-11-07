import { useState } from 'react';
import { ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';
import { Character } from '../types';

export const CharacterManager = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { characters, setCharacters } = useVideoStore();

  const addCharacter = () => {
    if (characters.length < 5) {
      setCharacters([...characters, { name: '', description: '' }]);
    }
  };

  const updateCharacter = (index: number, field: keyof Character, value: string) => {
    const updated = characters.map((char, i) =>
      i === index ? { ...char, [field]: value } : char
    );
    setCharacters(updated);
  };

  const removeCharacter = (index: number) => {
    setCharacters(characters.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="text-left">
          <h2 className="text-xl font-bold text-gray-900">Advanced: Character Consistency</h2>
          <p className="text-sm text-gray-600">
            Define main characters for consistent appearance
          </p>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>

      {isOpen && (
        <div className="px-6 pb-6 space-y-4 border-t border-gray-100">
          <div className="pt-6">
            {characters.map((character, index) => (
              <div key={index} className="mb-4 p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900">Character {index + 1}</h3>
                  <button
                    onClick={() => removeCharacter(index)}
                    className="text-red-600 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Character name"
                    value={character.name}
                    onChange={(e) => updateCharacter(index, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  <textarea
                    placeholder="Description (e.g., Sarah, 25 years old, brown hair, terrified expression, wearing hospital scrubs)"
                    value={character.description}
                    onChange={(e) => updateCharacter(index, 'description', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    rows={3}
                  />
                </div>
              </div>
            ))}
          </div>

          {characters.length < 5 && (
            <button
              onClick={addCharacter}
              className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-indigo-400 hover:bg-indigo-50 transition-colors flex items-center justify-center space-x-2 text-gray-600 hover:text-indigo-600"
            >
              <Plus className="w-5 h-5" />
              <span>Add Character</span>
            </button>
          )}

          <p className="text-sm text-gray-500">
            Add up to 5 main characters. More detailed descriptions result in better consistency.
          </p>
        </div>
      )}
    </div>
  );
};
