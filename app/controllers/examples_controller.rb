class ExamplesController < ApplicationController
  before_action :set_example, only: [:show]

  # GET /examples
  # GET /examples.json
  def index
    @examples = Example.all
  end

  # GET /examples/1
  # GET /examples/1.json
  def show
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_example
      @example = Example.find(params[:id])
    end
end
