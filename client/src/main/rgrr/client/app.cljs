(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            [clojure.pprint :as pp]
            ["@nivo/bar" :refer [ResponsiveBar]]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]
            [shadow.css :refer (css)]))

(def simulation-config
  {:nodes 100
   :epochs 10
   :resources_per_node 1
   :operations [{:type "preferential" :resources_added 10}]})

(defonce simulation-id (r/atom nil)) ; To store the ID of the created simulation

(def histogram-data (atom {}))
(def histogram-index (r/atom 0))
(def histogram-current (r/atom ()))

(defn create-and-fetch-simulation []
  (go
    (let [resp (async/<! (http/post "/simulations" {:json-params simulation-config}))
          id (:id (:body resp))]
      (reset! simulation-id id)
      (js/console.log (str "Created simulation with ID: " id))
      (async/<! (http/post (str "/simulations/" id "/run")))
      (let [resp (async/<! (http/get (str "/simulations/" @simulation-id "/histograms")))]
        (reset! histogram-data (:body resp))))))

(defonce root (delay (rdc/create-root (js/document.getElementById "app"))))

(defn get-histogram-data [index]
  (if (not (empty? @histogram-data))
   (let [labels (map #(/ (+ %1 %2) 2)
                     (:bin_edges @histogram-data)
                     (rest (:bin_edges @histogram-data)))
         data (nth (:epoch_distributions @histogram-data) index)]
     (map (fn [l d] {"id" (pp/cl-format nil "~,2f" l) "density" d}) labels data))
   []))

(defn render-header []
  [:div
   {:class (css :shadow {:color "red"})}
   ;; {:style {:width "100%" :text-align "center" :color "red"}}
   [:h2 "Epoch " @histogram-index]])

(defn render-chart []
  [:div {:style {:width "100%" :height "500px" :border "1px solid black"}}
   [:> ResponsiveBar
    {:data @histogram-current
     :keys ["density"]
     :height 500
     :width 400
     :defaultHeight 500
     :defaultWidth 400
     :margin {:top 50 :right 50 :bottom 50 :left 60}
     :padding 0.05
     :enableLabel false}]])

(defn render-controls []
  (let [epoch-max (- (count (:epoch_distributions @histogram-data)) 1)]
    [:div
     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index 0))
               :onClick #(if (> @histogram-index 0) (swap! histogram-index dec))}
      "Previous"]
     [:input {:type "text"
              :value @histogram-index
              :onChange (fn [e]
                          (let [new-epoch-str (-> e .-target .-value)
                                new-epoch (when (and new-epoch-str (re-matches #"\d+" new-epoch-str))
                                            (js/parseInt new-epoch-str 10))]
                            ;; Ensure the input is a valid integer and in range before updating the state
                            (when (and new-epoch (<= 0 new-epoch epoch-max))
                              (reset! histogram-index new-epoch))))}]
     [:button {:disabled (or (empty? @histogram-data) (= @histogram-index epoch-max))
               :onClick #(if (< @histogram-index epoch-max) (swap! histogram-index inc))}
      "Next"]]))

(defn render-histogram []
  (rdc/render @root
              [(fn []
                 [:div
                  [render-header]
                  [render-chart]
                  [render-controls]])]))

(defn update-current []
  (reset! histogram-current (get-histogram-data @histogram-index)))

(add-watch histogram-data :redisplay render-histogram)
(add-watch histogram-data :set-epoch update-current)
(add-watch histogram-index :set-epoch update-current)

(defn ^:export ^:dev/after-load init []
  ;; Create a simulation on application load
  (go (create-and-fetch-simulation)))
