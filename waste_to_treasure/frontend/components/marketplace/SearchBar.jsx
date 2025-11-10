'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'

/**
 * SearchBar component with category filters
 */
export default function SearchBar({ onSearch, onCategoryChange }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('Todos')

  const categories = [
    'Todos',
    'Metal',
    'Madera',
    'Plásticos',
    'Textil',
    'Vidrio',
    'Electrónico',
    'Papel/Cartón',
  ]

  const handleSearch = () => {
    onSearch?.(searchTerm)
  }

  const handleCategoryClick = (category) => {
    setSelectedCategory(category)
    onCategoryChange?.(category)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="flex w-full flex-col gap-6 rounded-lg bg-neutral-50 p-6 shadow-md">
      {/* Search Input */}
      <div className="flex gap-6">
        <div className="flex flex-1 items-center gap-2.5 rounded-lg border-2 border-neutral-300 bg-white px-4 py-1.5">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Buscar materiales por tipo, empresa o palabra clave..."
            className="flex-1 font-inter text-base text-black outline-none placeholder:text-neutral-500"
          />
        </div>
        <button
          onClick={handleSearch}
          className="rounded-lg bg-primary-500 px-5 py-4 font-inter text-base font-semibold text-white transition-colors hover:bg-primary-600"
        >
          Buscar
        </button>
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-6">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => handleCategoryClick(category)}
            className={`rounded-full px-4 py-2.5 font-inter text-base font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-primary-500 text-white'
                : 'border border-neutral-300 bg-neutral-100 text-black hover:bg-neutral-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>
    </div>
  )
}
