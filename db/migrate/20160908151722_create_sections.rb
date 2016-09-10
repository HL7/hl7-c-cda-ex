class CreateSections < ActiveRecord::Migration
  def change
    create_table :sections do |t|
      t.string   :name, limit: 80, null: false
      t.string   :section_type, limit: 20, null: false, default: 'sect'
      t.text     :narrative

      t.timestamps null: false
    end
  end
end
