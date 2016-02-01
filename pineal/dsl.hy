(defmacro loop [&rest body]
  `(do
     (import [pineal.core :as core])
     (import [math [*]])

     (defn --loop-- []
       ~@body)))


(defmacro color [&rest values]
  "
  Generate a color
  return a 4d signal

  r g b a -> r g b a
  r g b   -> r g b 1
  x a     -> x x x a
  x       -> x x x 1

  Example:
  (color 1 0.5)
  "
  `(let [[xs [~@values]]
         [l  (len xs)]]
     (cond
       [(= l 1) (let [[[x]        xs]] [x x x 1])]
       [(= l 2) (let [[[x a]      xs]] [x x x a])]
       [(= l 3) (let [[[r g b]    xs]] [r g b 1])]
       [(= l 4) (let [[[r g b  a] xs]] [r g b a])]
       [true [0 0 0 0]])))


(defmacro/g! osc-value [name path]
  `(defn ~name [&rest args]
     (setv ~g!mult (if args           (first args)  1))
     (setv ~g!add  (if (slice args 1) (second args) 0))

     ;; TODO handle multidimensional messages
     (setv ~g!value (first (.get --osc--
                                 (str '~path) [0.0])))
     (setv ~g!value
       (try (float ~g!value)
         (catch [] 0.0)))

     (-> ~g!value
       (* ~g!mult) (+ ~g!add))))


(defmacro/g! osc-send [value path]
  `(do
     (import liblo)
     (liblo.send --target-- (str '~path) ~value)))


(defmacro set-attrs [entity &rest attrs]
  "
  Set entity attributes
  internal
  "
  (when attrs
    `(let [[name   (str '~(first attrs))]
           [value  ~(second attrs)]
           [signal (apply core.Signal (flatten [value]))]]
       (core.attribute ~entity name signal)
       (set-attrs ~entity ~@(slice attrs 2)))))


(defn args:attrs [args]
  "
  Split args from attributes, using the : separator
  return the [args attrs] tuple
  "
  (if (in ': args)
    (let [[i     (.index args ':)]
          [attrs (rest (drop i args))]
          [args*       (take i args)]]
      [args* attrs])
    [args []]))


(defmacro/g! window [name body]
  "
  Create and update a window called `name`
  the body should be a sequence of drawable entities

  Example:
  (window main-window
          (polygon ...)
          ...)
  "
  `(do
     (setv ~g!window (-> '~name
                       str core.window))

     (core.render ~g!window
                  ~body)))


(defmacro/g! layer [name body]
  "
  Offscreen drawing
  draw on an layer

  Example:
  (layer layer-1
         something ...)
  "
  `(do
     (setv ~g!layer (-> '~name str core.layer))
     (core.render ~g!layer
                  ~body)))


(defmacro/g! draw [name]
  "
  Draw a layer
  "
  `(do
     (setv ~g!layer (-> '~name str core.layer))
     ~g!layer))


(defmacro/g! alias [name body]
  "
  Alias to an entity

  Example:
  (alias red-square
         (polygon 4
                  :
                  fill (color 1 0 0)))

  And then:
  (red-square)
  "
  `(do
     (setv ~g!entity ~body)

     (defn ~name [&rest args]
       (setv ~g!mult (if args           (first args)  1))
       (setv ~g!add  (if (slice args 1) (second args) 0))

       ~g!entity)))


(defmacro/g! polygon [n &rest args]
  "
  Regular polygon with `n` sides

  Attributes:
  - [line w] stroke width
  - [rotation rad]
  - [radius r]
  - [position x y z]
  - [fill color]
  - [stroke color]

  Example:
  (polygon 4
           :
           radius 2
           stroke (color 0.5 0 0))
  "
  (setv [args* attrs] (args:attrs args))
  `(do
     (setv ~g!entity (core.polygon ~n))
     (set-attrs ~g!entity ~@attrs)
     ~g!entity))
