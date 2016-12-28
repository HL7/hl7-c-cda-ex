class SectionsController < ApplicationController
  before_action :set_section, only: [:show]

  # GET /sections
  # GET /sections.json
  def index
    @sections = Section.all.ordered_by_name
  end

  # GET /sections/1
  # GET /sections/1.json
  def show
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_section
      @section = Section.find(params[:id])
    end
end
